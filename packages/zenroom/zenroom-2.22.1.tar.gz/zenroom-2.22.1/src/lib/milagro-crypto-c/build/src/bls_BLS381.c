/*
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
*/

/* Boneh-Lynn-Shacham signature 128-bit API */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "bls_BLS381.h"

// Polynomial interpolation coefficients
static void recover_coefficients(int k, octet* X, BIG_384_29* coefs)
{
    BIG_384_29 r;
    BIG_384_29_rcopy(r,CURVE_Order_BLS381);

    BIG_384_29 x2[k];

    for(int i=0; i<k; i++)
    {
        BIG_384_29_fromBytes(x2[i],X[i].val);
    }

    // Compute numerators in place using partial products
    // to achieve it in O(n)
    // c_i = x_0 * ... * x_(i-1) * x_(i+1) * ... * x_(k-1)

    // Compute partial left products
    // leave c_0 alone since it only has a right partial product
    BIG_384_29_copy(coefs[1], x2[0]);

    for(int i=2; i < k; i++)
    {
        // lp_i = x_0 * ... * x_(i-1) = lp_(i-1) * x_(i-1)
        BIG_384_29_modmul(coefs[i], coefs[i-1], x2[i-1], r);
    }

    // Compute partial right products and combine

    // Store partial right products in c_0 so at the end
    // of the procedure c_0 = x_1 * ... x_(k-1)
    BIG_384_29_copy(coefs[0], x2[k-1]);

    for(int i=k-2; i > 0; i--)
    {
        // c_i = lp_i * rp_i
        BIG_384_29_modmul(coefs[i], coefs[i], coefs[0], r);

        // rp_(i-1) = x_i * ... * x_k = x_i * rp_i
        BIG_384_29_modmul(coefs[0], coefs[0], x2[i], r);
    }

    BIG_384_29 cneg;
    BIG_384_29 denominator;
    BIG_384_29 s;

    for(int i=0; i<k; i++)
    {
        BIG_384_29_one(denominator);

        // cneg = -x_i mod r
        BIG_384_29_sub(cneg, r, x2[i]);

        for(int j=0; j<k; j++)
        {
            if (i != j)
            {
                // denominator = denominator * (x_j - x_i)
                BIG_384_29_add(s,x2[j],cneg);
                BIG_384_29_modmul(denominator,denominator,s,r);
            }
        }

        BIG_384_29_moddiv(coefs[i], coefs[i], denominator, r);
    }
}

/* hash a message, M, to an ECP point, using SHA3 */
static void BLS_HASHIT(ECP_BLS381 *P,octet *M)
{
    int i;
    int j;
    sha3 hs;
    char h[MODBYTES_384_29];
    octet HM= {0,sizeof(h),h};
    SHA3_init(&hs,SHAKE256);
    for (i=0; i<M->len; i++)
    {
        j = (unsigned char) M->val[i];
        SHA3_process(&hs,j);
    }
    SHA3_shake(&hs,HM.val,MODBYTES_384_29);
    HM.len=MODBYTES_384_29;
    ECP_BLS381_mapit(P,&HM);
}

/* generate key pair, private key S, public key W */
int BLS_BLS381_KEY_PAIR_GENERATE(csprng *RNG,octet* S,octet *W)
{
    ECP2_BLS381 G;
    BIG_384_29 s,q;
    BIG_384_29_rcopy(q,CURVE_Order_BLS381);
    ECP2_BLS381_generator(&G);

    if (RNG!=NULL)
    {
        BIG_384_29_randomnum(s,q,RNG);
        BIG_384_29_toBytes(S->val,s);
        S->len=MODBYTES_384_29;
    }
    else
    {
        S->len=MODBYTES_384_29;
        BIG_384_29_fromBytes(s,S->val);
    }

    PAIR_BLS381_G2mul(&G,s);
    ECP2_BLS381_toOctet(W,&G);

    return BLS_OK;
}

/* Sign message M using private key S to produce signature SIG */
int BLS_BLS381_SIGN(octet *SIG,octet *M,octet *S)
{
    BIG_384_29 s;
    ECP_BLS381 D;
    BLS_HASHIT(&D,M);
    BIG_384_29_fromBytes(s,S->val);
    PAIR_BLS381_G1mul(&D,s);
    // compress output
    ECP_BLS381_toOctet(SIG,&D,true);

    return BLS_OK;
}

/* Verify signature of message M, the signature SIG, and the public key W */
int BLS_BLS381_VERIFY(octet *SIG,octet *M,octet *W)
{
    FP12_BLS381 v;
    ECP2_BLS381 G,PK;
    ECP_BLS381 D,HM;
    BLS_HASHIT(&HM,M);

    if (!ECP_BLS381_fromOctet(&D,SIG))
    {
        return BLS_INVALID_G1;
    }

    ECP2_BLS381_generator(&G);

    if (!ECP2_BLS381_fromOctet(&PK,W))
    {
        return BLS_INVALID_G2;
    }
    ECP_BLS381_neg(&D);

    PAIR_BLS381_double_ate(&v,&G,&D,&PK,&HM);
    PAIR_BLS381_fexp(&v);

    if (!FP12_BLS381_isunity(&v))
    {
        return BLS_FAIL;
    }
    return BLS_OK;
}

/* R=R1+R2 in group G1 */
int BLS_BLS381_ADD_G1(octet *R1,octet *R2,octet *R)
{
    ECP_BLS381 P;
    ECP_BLS381 T;

    if (!ECP_BLS381_fromOctet(&P,R1))
    {
        return BLS_INVALID_G1;
    }

    if (!ECP_BLS381_fromOctet(&T,R2))
    {
        return BLS_INVALID_G1;
    }

    ECP_BLS381_add(&P,&T);
    ECP_BLS381_toOctet(R,&P,true);

    return BLS_OK;
}

/* W=W1+W2 in group G2 */
int BLS_BLS381_ADD_G2(octet *W1,octet *W2,octet *W)
{
    ECP2_BLS381 Q;
    ECP2_BLS381 T;

    if (!ECP2_BLS381_fromOctet(&Q,W1))
    {
        return BLS_INVALID_G2;
    }

    if (!ECP2_BLS381_fromOctet(&T,W2))
    {
        return BLS_INVALID_G2;
    }

    ECP2_BLS381_add(&Q,&T);
    ECP2_BLS381_toOctet(W,&Q);

    return BLS_OK;
}

int BLS_BLS381_MAKE_SHARES(int k, int n, csprng *RNG, octet* X, octet* Y, octet* SKI, octet* SKO)
{
    BIG_384_29 r;
    BIG_384_29_rcopy(r,CURVE_Order_BLS381);

    // Generate polynomial: f(x) = a_0 + a_1x + a_2x^2 ... a_{k-1}x^{k-1}
    BIG_384_29 poly[k];
    for(int i=0; i<k; i++)
    {
        BIG_384_29_randomnum(poly[i],r,RNG);
    }

    // Use predefined secret
    if (SKI != NULL)
    {
        BIG_384_29_fromBytes(poly[0],SKI->val);
    }

    /* Calculate f(x) = a_0 + a_1x + a_2x^2 ... a_{k-1}x^{k-1}
       a0 is the secret */
    BIG_384_29 x;
    BIG_384_29_zero(x);

    BIG_384_29 y;

    for(int j=0; j<n; j++)
    {
        BIG_384_29_inc(x,1);

        // Output X shares
        BIG_384_29_toBytes(X[j].val,x);
        X[j].len = MODBYTES_384_29;

        // y is the accumulator
        BIG_384_29_zero(y);

        for(int i=k-1; i>=0; i--)
        {
            BIG_384_29_modmul(y,y,x,r);
            BIG_384_29_add(y,y,poly[i]);
        }

        // Normalise input for comp
        BIG_384_29_norm(y);
        if(BIG_384_29_comp(y,r) == 1)
        {
            BIG_384_29_sub(y,y,r);
        }

        // Output Y shares
        BIG_384_29_toBytes(Y[j].val,y);
        Y[j].len = MODBYTES_384_29;
    }

    // Output secret
    BIG_384_29_toBytes(SKO->val,poly[0]);
    SKO->len = MODBYTES_384_29;

    return BLS_OK;
}

int BLS_BLS381_RECOVER_SECRET(int k, octet* X, octet* Y, octet* SK)
{
    BIG_384_29 r;
    BIG_384_29_rcopy(r,CURVE_Order_BLS381);

    BIG_384_29 y;
    BIG_384_29 coefs[k];

    BIG_384_29 secret;
    BIG_384_29 prod;
    BIG_384_29_zero(secret);

    recover_coefficients(k, X, coefs);

    for(int i=0; i<k; i++)
    {
        BIG_384_29_fromBytes(y,Y[i].val);

        BIG_384_29_modmul(prod,y,coefs[i],r);
        BIG_384_29_add(secret, secret, prod);

        // Normalise input for comp
        BIG_384_29_norm(secret);
        if (BIG_384_29_comp(secret,r) == 1)
        {
            BIG_384_29_sub(secret,secret,r);
        }
    }

    // Output secret
    BIG_384_29_toBytes(SK->val,secret);
    SK->len = MODBYTES_384_29;

    return BLS_OK;
}

int BLS_BLS381_RECOVER_SIGNATURE(int k, octet* X, octet* Y, octet* SIG)
{
    BIG_384_29 coefs[k];
    ECP_BLS381 y;

    ECP_BLS381 sig;
    ECP_BLS381_inf(&sig);

    recover_coefficients(k, X, coefs);

    for(int i=0; i<k; i++)
    {
        if (!ECP_BLS381_fromOctet(&y,&Y[i]))
        {
            return BLS_INVALID_G1;
        }

        PAIR_BLS381_G1mul(&y,coefs[i]);
        ECP_BLS381_add(&sig,&y);
    }

    ECP_BLS381_toOctet(SIG, &sig, true);

    return BLS_OK;
}
