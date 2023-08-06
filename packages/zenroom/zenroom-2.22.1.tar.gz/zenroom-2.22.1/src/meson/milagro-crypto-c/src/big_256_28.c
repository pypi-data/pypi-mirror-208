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

/* AMCL basic functions for BIG type */
/* SU=m, SU is Stack Usage */

#include "big_256_28.h"

/* test a=0? */
int BIG_256_28_iszilch(BIG_256_28 a)
{
    int i;
    for (i=0; i<NLEN_256_28; i++)
        if (a[i]!=0) return 0;
    return 1;
}

/* test a=1? */
int BIG_256_28_isunity(BIG_256_28 a)
{
    int i;
    for(i=1; i<NLEN_256_28; i++)
        if (a[i]!=0) return 0;
    if (a[0]!=1) return 0;
    return 1;
}

/* test a=0? */
int BIG_256_28_diszilch(DBIG_256_28 a)
{
    int i;
    for (i=0; i<DNLEN_256_28; i++)
        if (a[i]!=0) return 0;
    return 1;
}

/* SU= 56 */
/* output a */
void BIG_256_28_output(BIG_256_28 a)
{
    BIG_256_28 b;
    int i,len;
    len=BIG_256_28_nbits(a);
    if (len%4==0) len/=4;
    else
    {
        len/=4;
        len++;
    }
    if (len<MODBYTES_256_28*2) len=MODBYTES_256_28*2;

    for (i=len-1; i>=0; i--)
    {
        BIG_256_28_copy(b,a);
        BIG_256_28_shr(b,i*4);
        printf("%01x",(unsigned int) b[0]&15);
    }
}

/* SU= 16 */
void BIG_256_28_rawoutput(BIG_256_28 a)
{
    int i;
    printf("(");
    for (i=0; i<NLEN_256_28-1; i++)
#if CHUNK==64
        printf("%"PRIxMAX",",(uintmax_t) a[i]);
    printf("%"PRIxMAX")",(uintmax_t) a[NLEN_256_28-1]);
#else
        printf("%x,",(unsigned int) a[i]);
    printf("%x)",(unsigned int) a[NLEN_256_28-1]);
#endif
}

/* Swap a and b if d=1 */
void BIG_256_28_cswap(BIG_256_28 a,BIG_256_28 b,int d)
{
    int i;
    chunk t,c=d;
    c=~(c-1);
#ifdef DEBUG_NORM
    for (i=0; i<NLEN_256_28+2; i++)
#else
    for (i=0; i<NLEN_256_28; i++)
#endif
    {
        t=c&(a[i]^b[i]);
        a[i]^=t;
        b[i]^=t;
    }
}

/* Move b to a if d=1 */
void BIG_256_28_cmove(BIG_256_28 f,BIG_256_28 g,int d)
{
    int i;
    chunk b=(chunk)-d;
#ifdef DEBUG_NORM
    for (i=0; i<NLEN_256_28+2; i++)
#else
    for (i=0; i<NLEN_256_28; i++)
#endif
    {
        f[i]^=(f[i]^g[i])&b;
    }
}

/* Move g to f if d=1 */
void BIG_256_28_dcmove(DBIG_256_28 f,DBIG_256_28 g,int d)
{
    int i;
    chunk b=(chunk)-d;
#ifdef DEBUG_NORM
    for (i=0; i<DNLEN_256_28+2; i++)
#else
    for (i=0; i<DNLEN_256_28; i++)
#endif
    {
        f[i]^=(f[i]^g[i])&b;
    }
}

/* convert BIG to/from bytes */
/* SU= 64 */
void BIG_256_28_toBytes(char *b,BIG_256_28 a)
{
    int i;
    BIG_256_28 c;
    BIG_256_28_copy(c,a);
    BIG_256_28_norm(c);
    for (i=MODBYTES_256_28-1; i>=0; i--)
    {
        b[i]=c[0]&0xff;
        BIG_256_28_fshr(c,8);
    }
}

/* SU= 16 */
void BIG_256_28_fromBytes(BIG_256_28 a,char *b)
{
    int i;
    BIG_256_28_zero(a);
    for (i=0; i<MODBYTES_256_28; i++)
    {
        BIG_256_28_fshl(a,8);
        a[0]+=(int)(unsigned char)b[i];
    }
#ifdef DEBUG_NORM
    a[MPV_256_28]=1;
    a[MNV_256_28]=0;
#endif
}

void BIG_256_28_fromBytesLen(BIG_256_28 a,char *b,int s)
{
    int i,len=s;
    BIG_256_28_zero(a);

    if (len>MODBYTES_256_28) len=MODBYTES_256_28;
    for (i=0; i<len; i++)
    {
        BIG_256_28_fshl(a,8);
        a[0]+=(int)(unsigned char)b[i];
    }
#ifdef DEBUG_NORM
    a[MPV_256_28]=1;
    a[MNV_256_28]=0;
#endif
}



/* SU= 88 */
void BIG_256_28_doutput(DBIG_256_28 a)
{
    DBIG_256_28 b;
    int i,len;
    BIG_256_28_dnorm(a);
    len=BIG_256_28_dnbits(a);
    if (len%4==0) len/=4;
    else
    {
        len/=4;
        len++;
    }

    for (i=len-1; i>=0; i--)
    {
        BIG_256_28_dcopy(b,a);
        BIG_256_28_dshr(b,i*4);
        printf("%01x",(unsigned int) b[0]&15);
    }
}


void BIG_256_28_drawoutput(DBIG_256_28 a)
{
    int i;
    printf("(");
    for (i=0; i<DNLEN_256_28-1; i++)
#if CHUNK==64
        printf("%"PRIxMAX",",(uintmax_t) a[i]);
    printf("%"PRIxMAX")",(uintmax_t) a[DNLEN_256_28-1]);
#else
        printf("%x,",(unsigned int) a[i]);
    printf("%x)",(unsigned int) a[DNLEN_256_28-1]);
#endif
}

/* Copy b=a */
void BIG_256_28_copy(BIG_256_28 b,BIG_256_28 a)
{
    int i;
    for (i=0; i<NLEN_256_28; i++)
        b[i]=a[i];
#ifdef DEBUG_NORM
    b[MPV_256_28]=a[MPV_256_28];
    b[MNV_256_28]=a[MNV_256_28];
#endif
}

/* Copy from ROM b=a */
void BIG_256_28_rcopy(BIG_256_28 b,const BIG_256_28 a)
{
    int i;
    for (i=0; i<NLEN_256_28; i++)
        b[i]=a[i];
#ifdef DEBUG_NORM
    b[MPV_256_28]=1;
    b[MNV_256_28]=0;
#endif
}

/* double length DBIG copy b=a */
void BIG_256_28_dcopy(DBIG_256_28 b,DBIG_256_28 a)
{
    int i;
    for (i=0; i<DNLEN_256_28; i++)
        b[i]=a[i];
#ifdef DEBUG_NORM
    b[DMPV_256_28]=a[DMPV_256_28];
    b[DMNV_256_28]=a[DMNV_256_28];
#endif
}

/* Copy BIG to bottom half of DBIG */
void BIG_256_28_dscopy(DBIG_256_28 b,BIG_256_28 a)
{
    int i;
    for (i=0; i<NLEN_256_28-1; i++)
        b[i]=a[i];

    b[NLEN_256_28-1]=a[NLEN_256_28-1]&BMASK_256_28; /* top word normalized */
    b[NLEN_256_28]=a[NLEN_256_28-1]>>BASEBITS_256_28;

    for (i=NLEN_256_28+1; i<DNLEN_256_28; i++) b[i]=0;
#ifdef DEBUG_NORM
    b[DMPV_256_28]=a[MPV_256_28];
    b[DMNV_256_28]=a[MNV_256_28];
#endif
}

/* Copy BIG to top half of DBIG */
void BIG_256_28_dsucopy(DBIG_256_28 b,BIG_256_28 a)
{
    int i;
    for (i=0; i<NLEN_256_28; i++)
        b[i]=0;
    for (i=NLEN_256_28; i<DNLEN_256_28; i++)
        b[i]=a[i-NLEN_256_28];
#ifdef DEBUG_NORM
    b[DMPV_256_28]=a[MPV_256_28];
    b[DMNV_256_28]=a[MNV_256_28];
#endif
}

/* Copy bottom half of DBIG to BIG */
void BIG_256_28_sdcopy(BIG_256_28 b,DBIG_256_28 a)
{
    int i;
    for (i=0; i<NLEN_256_28; i++)
        b[i]=a[i];
#ifdef DEBUG_NORM
    b[MPV_256_28]=a[DMPV_256_28];
    b[MNV_256_28]=a[DMNV_256_28];
#endif
}

/* Copy top half of DBIG to BIG */
void BIG_256_28_sducopy(BIG_256_28 b,DBIG_256_28 a)
{
    int i;
    for (i=0; i<NLEN_256_28; i++)
        b[i]=a[i+NLEN_256_28];
#ifdef DEBUG_NORM
    b[MPV_256_28]=a[DMPV_256_28];
    b[MNV_256_28]=a[DMNV_256_28];

#endif
}

/* Set a=0 */
void BIG_256_28_zero(BIG_256_28 a)
{
    int i;
    for (i=0; i<NLEN_256_28; i++)
        a[i]=0;
#ifdef DEBUG_NORM
    a[MPV_256_28]=a[MNV_256_28]=0;
#endif
}

void BIG_256_28_dzero(DBIG_256_28 a)
{
    int i;
    for (i=0; i<DNLEN_256_28; i++)
        a[i]=0;
#ifdef DEBUG_NORM
    a[DMPV_256_28]=a[DMNV_256_28]=0;
#endif
}

/* set a=1 */
void BIG_256_28_one(BIG_256_28 a)
{
    int i;
    a[0]=1;
    for (i=1; i<NLEN_256_28; i++)
        a[i]=0;
#ifdef DEBUG_NORM
    a[MPV_256_28]=1;
    a[MNV_256_28]=0;
#endif
}



/* Set c=a+b */
/* SU= 8 */
void BIG_256_28_add(BIG_256_28 c,BIG_256_28 a,BIG_256_28 b)
{
    int i;
    for (i=0; i<NLEN_256_28; i++)
        c[i]=a[i]+b[i];
#ifdef DEBUG_NORM
    c[MPV_256_28]=a[MPV_256_28]+b[MPV_256_28];
    c[MNV_256_28]=a[MNV_256_28]+b[MNV_256_28];
    if (c[MPV_256_28]>NEXCESS_256_28)  printf("add problem - positive digit overflow %d\n",c[MPV_256_28]);
    if (c[MNV_256_28]>NEXCESS_256_28)  printf("add problem - negative digit overflow %d\n",c[MNV_256_28]);

#endif
}

/* Set c=a or b */
void BIG_256_28_or(BIG_256_28 c,BIG_256_28 a,BIG_256_28 b)
{
    int i;
    BIG_256_28_norm(a);
    BIG_256_28_norm(b);
    for (i=0; i<NLEN_256_28; i++)
        c[i]=a[i]|b[i];
#ifdef DEBUG_NORM
    c[MPV_256_28]=1;
    c[MNV_256_28]=0;
#endif
}


/* Set c=c+d */
void BIG_256_28_inc(BIG_256_28 c,int d)
{
    BIG_256_28_norm(c);
    c[0]+=(chunk)d;
#ifdef DEBUG_NORM
    c[MPV_256_28]+=1;
#endif
}

/* Set c=a-b */
/* SU= 8 */
void BIG_256_28_sub(BIG_256_28 c,BIG_256_28 a,BIG_256_28 b)
{
    int i;
    for (i=0; i<NLEN_256_28; i++)
        c[i]=a[i]-b[i];
#ifdef DEBUG_NORM
    c[MPV_256_28]=a[MPV_256_28]+b[MNV_256_28];
    c[MNV_256_28]=a[MNV_256_28]+b[MPV_256_28];
    if (c[MPV_256_28]>NEXCESS_256_28)  printf("sub problem - positive digit overflow %d\n",c[MPV_256_28]);
    if (c[MNV_256_28]>NEXCESS_256_28)  printf("sub problem - negative digit overflow %d\n",c[MNV_256_28]);

#endif
}

/* SU= 8 */

void BIG_256_28_dsub(DBIG_256_28 c,DBIG_256_28 a,DBIG_256_28 b)
{
    int i;
    for (i=0; i<DNLEN_256_28; i++)
        c[i]=a[i]-b[i];
#ifdef DEBUG_NORM
    c[DMPV_256_28]=a[DMPV_256_28]+b[DMNV_256_28];
    c[DMNV_256_28]=a[DMNV_256_28]+b[DMPV_256_28];
    if (c[DMPV_256_28]>NEXCESS_256_28)  printf("double sub problem - positive digit overflow %d\n",c[DMPV_256_28]);
    if (c[DMNV_256_28]>NEXCESS_256_28)  printf("double sub problem - negative digit overflow %d\n",c[DMNV_256_28]);
#endif
}

void BIG_256_28_dadd(DBIG_256_28 c,DBIG_256_28 a,DBIG_256_28 b)
{
    int i;
    for (i=0; i<DNLEN_256_28; i++)
        c[i]=a[i]+b[i];
#ifdef DEBUG_NORM
    c[DMPV_256_28]=a[DMPV_256_28]+b[DMNV_256_28];
    c[DMNV_256_28]=a[DMNV_256_28]+b[DMPV_256_28];
    if (c[DMPV_256_28]>NEXCESS_256_28)  printf("double add problem - positive digit overflow %d\n",c[DMPV_256_28]);
    if (c[DMNV_256_28]>NEXCESS_256_28)  printf("double add problem - negative digit overflow %d\n",c[DMNV_256_28]);
#endif
}

/* Set c=c-1 */
void BIG_256_28_dec(BIG_256_28 c,int d)
{
    BIG_256_28_norm(c);
    c[0]-=(chunk)d;
#ifdef DEBUG_NORM
    c[MNV_256_28]+=1;
#endif
}

/* multiplication r=a*c by c<=NEXCESS_256_28 */
void BIG_256_28_imul(BIG_256_28 r,BIG_256_28 a,int c)
{
    int i;
    for (i=0; i<NLEN_256_28; i++) r[i]=a[i]*c;
#ifdef DEBUG_NORM
    r[MPV_256_28]=a[MPV_256_28]*c;
    r[MNV_256_28]=a[MNV_256_28]*c;
    if (r[MPV_256_28]>NEXCESS_256_28)  printf("int mul problem - positive digit overflow %d\n",r[MPV_256_28]);
    if (r[MNV_256_28]>NEXCESS_256_28)  printf("int mul problem - negative digit overflow %d\n",r[MNV_256_28]);

#endif
}

/* multiplication r=a*c by larger integer - c<=FEXCESS */
/* SU= 24 */
chunk BIG_256_28_pmul(BIG_256_28 r,BIG_256_28 a,int c)
{
    int i;
    chunk ak,carry=0;
    for (i=0; i<NLEN_256_28; i++)
    {
        ak=a[i];
        r[i]=0;
        carry=muladd_256_28(ak,(chunk)c,carry,&r[i]);
    }
#ifdef DEBUG_NORM
    r[MPV_256_28]=1;
    r[MNV_256_28]=0;
#endif
    return carry;
}

/* r/=3 */
/* SU= 16 */
int BIG_256_28_div3(BIG_256_28 r)
{
    int i;
    chunk ak,base,carry=0;
    BIG_256_28_norm(r);
    base=((chunk)1<<BASEBITS_256_28);
    for (i=NLEN_256_28-1; i>=0; i--)
    {
        ak=(carry*base+r[i]);
        r[i]=ak/3;
        carry=ak%3;
    }
    return (int)carry;
}

/* multiplication c=a*b by even larger integer b>FEXCESS, resulting in DBIG */
/* SU= 24 */
void BIG_256_28_pxmul(DBIG_256_28 c,BIG_256_28 a,int b)
{
    int j;
    chunk carry;
    BIG_256_28_dzero(c);
    carry=0;
    for (j=0; j<NLEN_256_28; j++)
        carry=muladd_256_28(a[j],(chunk)b,carry,&c[j]);
    c[NLEN_256_28]=carry;
#ifdef DEBUG_NORM
    c[DMPV_256_28]=1;
    c[DMNV_256_28]=0;
#endif
}

/* .. if you know the result will fit in a BIG, c must be distinct from a and b */
/* SU= 40 */
void BIG_256_28_smul(BIG_256_28 c,BIG_256_28 a,BIG_256_28 b)
{
    int i,j;
    chunk carry;

    BIG_256_28_zero(c);
    for (i=0; i<NLEN_256_28; i++)
    {
        carry=0;
        for (j=0; j<NLEN_256_28; j++)
        {
            if (i+j<NLEN_256_28)
                carry=muladd_256_28(a[i],b[j],carry,&c[i+j]);
        }
    }
#ifdef DEBUG_NORM
    c[MPV_256_28]=1;
    c[MNV_256_28]=0;
#endif

}

/* Set c=a*b */
/* SU= 72 */
void BIG_256_28_mul(DBIG_256_28 c,BIG_256_28 a,BIG_256_28 b)
{
    int i;
#ifdef dchunk
    dchunk t,co;
    dchunk s;
    dchunk d[NLEN_256_28];
    int k;
#endif

#ifdef DEBUG_NORM
    if ((a[MPV_256_28]!=1 && a[MPV_256_28]!=0) || a[MNV_256_28]!=0) printf("First input to mul not normed\n");
    if ((b[MPV_256_28]!=1 && b[MPV_256_28]!=0) || b[MNV_256_28]!=0) printf("Second input to mul not normed\n");
#endif

    /* Faster to Combafy it.. Let the compiler unroll the loops! */

#ifdef COMBA

    /* faster psuedo-Karatsuba method */
#ifdef UNWOUND

    /* Insert output of faster.c here */

#else
    for (i=0; i<NLEN_256_28; i++)
        d[i]=(dchunk)a[i]*b[i];

    s=d[0];
    t=s;
    c[0]=(chunk)t&BMASK_256_28;
    co=t>>BASEBITS_256_28;

    for (k=1; k<NLEN_256_28; k++)
    {
        s+=d[k];
        t=co+s;
        for (i=k; i>=1+k/2; i--) t+=(dchunk)(a[i]-a[k-i])*(b[k-i]-b[i]);
        c[k]=(chunk)t&BMASK_256_28;
        co=t>>BASEBITS_256_28;
    }
    for (k=NLEN_256_28; k<2*NLEN_256_28-1; k++)
    {
        s-=d[k-NLEN_256_28];
        t=co+s;
        for (i=NLEN_256_28-1; i>=1+k/2; i--) t+=(dchunk)(a[i]-a[k-i])*(b[k-i]-b[i]);
        c[k]=(chunk)t&BMASK_256_28;
        co=t>>BASEBITS_256_28;
    }
    c[2*NLEN_256_28-1]=(chunk)co;

#endif

#else
    int j;
    chunk carry;
    BIG_256_28_dzero(c);
    for (i=0; i<NLEN_256_28; i++)
    {
        carry=0;
        for (j=0; j<NLEN_256_28; j++)
            carry=muladd_256_28(a[i],b[j],carry,&c[i+j]);

        c[NLEN_256_28+i]=carry;
    }

#endif

#ifdef DEBUG_NORM
    c[DMPV_256_28]=1;
    c[DMNV_256_28]=0;
#endif
}

/* Set c=a*a */
/* SU= 80 */
void BIG_256_28_sqr(DBIG_256_28 c,BIG_256_28 a)
{
    int i,j;
#ifdef dchunk
    dchunk t,co;
#endif

#ifdef DEBUG_NORM
    if ((a[MPV_256_28]!=1 && a[MPV_256_28]!=0) || a[MNV_256_28]!=0) printf("Input to sqr not normed\n");
#endif
    /* Note 2*a[i] in loop below and extra addition */

#ifdef COMBA

#ifdef UNWOUND

    /* Insert output of faster.c here */

#else


    t=(dchunk)a[0]*a[0];
    c[0]=(chunk)t&BMASK_256_28;
    co=t>>BASEBITS_256_28;

    for (j=1; j<NLEN_256_28-1; )
    {
        t=(dchunk)a[j]*a[0];
        for (i=1; i<(j+1)/2; i++)
        {
            t+=(dchunk)a[j-i]*a[i];
        }
        t+=t;
        t+=co;
        c[j]=(chunk)t&BMASK_256_28;
        co=t>>BASEBITS_256_28;
        j++;
        t=(dchunk)a[j]*a[0];
        for (i=1; i<(j+1)/2; i++)
        {
            t+=(dchunk)a[j-i]*a[i];
        }
        t+=t;
        t+=co;
        t+=(dchunk)a[j/2]*a[j/2];
        c[j]=(chunk)t&BMASK_256_28;
        co=t>>BASEBITS_256_28;
        j++;
    }

    for (j=NLEN_256_28-1+NLEN_256_28%2; j<DNLEN_256_28-3; )
    {
        t=(dchunk)a[NLEN_256_28-1]*a[j-NLEN_256_28+1];
        for (i=j-NLEN_256_28+2; i<(j+1)/2; i++)
        {
            t+=(dchunk)a[j-i]*a[i];
        }
        t+=t;
        t+=co;
        c[j]=(chunk)t&BMASK_256_28;
        co=t>>BASEBITS_256_28;
        j++;
        t=(dchunk)a[NLEN_256_28-1]*a[j-NLEN_256_28+1];
        for (i=j-NLEN_256_28+2; i<(j+1)/2; i++)
        {
            t+=(dchunk)a[j-i]*a[i];
        }
        t+=t;
        t+=co;
        t+=(dchunk)a[j/2]*a[j/2];
        c[j]=(chunk)t&BMASK_256_28;
        co=t>>BASEBITS_256_28;
        j++;
    }

    t=(dchunk)a[NLEN_256_28-2]*a[NLEN_256_28-1];
    t+=t;
    t+=co;
    c[DNLEN_256_28-3]=(chunk)t&BMASK_256_28;
    co=t>>BASEBITS_256_28;

    t=(dchunk)a[NLEN_256_28-1]*a[NLEN_256_28-1]+co;
    c[DNLEN_256_28-2]=(chunk)t&BMASK_256_28;
    co=t>>BASEBITS_256_28;
    c[DNLEN_256_28-1]=(chunk)co;


#endif

#else
    chunk carry;
    BIG_256_28_dzero(c);
    for (i=0; i<NLEN_256_28; i++)
    {
        carry=0;
        for (j=i+1; j<NLEN_256_28; j++)
            carry=muladd_256_28(a[i],a[j],carry,&c[i+j]);
        c[NLEN_256_28+i]=carry;
    }

    for (i=0; i<DNLEN_256_28; i++) c[i]*=2;

    for (i=0; i<NLEN_256_28; i++)
        c[2*i+1]+=muladd_256_28(a[i],a[i],0,&c[2*i]);

    BIG_256_28_dnorm(c);
#endif


#ifdef DEBUG_NORM
    c[DMPV_256_28]=1;
    c[DMNV_256_28]=0;
#endif

}

/* Montgomery reduction */
void BIG_256_28_monty(BIG_256_28 a,BIG_256_28 md,chunk MC,DBIG_256_28 d)
{
    int i,k;

#ifdef dchunk
    dchunk t,c,s;
    dchunk dd[NLEN_256_28];
    chunk v[NLEN_256_28];
#endif

#ifdef COMBA

#ifdef UNWOUND

    /* Insert output of faster.c here */

#else

    t=d[0];
    v[0]=((chunk)t*MC)&BMASK_256_28;
    t+=(dchunk)v[0]*md[0];
    c=(t>>BASEBITS_256_28)+d[1];
    s=0;

    for (k=1; k<NLEN_256_28; k++)
    {
        t=c+s+(dchunk)v[0]*md[k];
        for (i=k-1; i>k/2; i--) t+=(dchunk)(v[k-i]-v[i])*(md[i]-md[k-i]);
        v[k]=((chunk)t*MC)&BMASK_256_28;
        t+=(dchunk)v[k]*md[0];
        c=(t>>BASEBITS_256_28)+d[k+1];
        dd[k]=(dchunk)v[k]*md[k];
        s+=dd[k];
    }
    for (k=NLEN_256_28; k<2*NLEN_256_28-1; k++)
    {
        t=c+s;
        for (i=NLEN_256_28-1; i>=1+k/2; i--) t+=(dchunk)(v[k-i]-v[i])*(md[i]-md[k-i]);
        a[k-NLEN_256_28]=(chunk)t&BMASK_256_28;
        c=(t>>BASEBITS_256_28)+d[k+1];
        s-=dd[k-NLEN_256_28+1];
    }
    a[NLEN_256_28-1]=(chunk)c&BMASK_256_28;

#endif



#else
    int j;
    chunk m,carry;
    for (i=0; i<NLEN_256_28; i++)
    {
        if (MC==-1) m=(-d[i])&BMASK_256_28;
        else
        {
            if (MC==1) m=d[i];
            else m=(MC*d[i])&BMASK_256_28;
        }
        carry=0;
        for (j=0; j<NLEN_256_28; j++)
            carry=muladd_256_28(m,md[j],carry,&d[i+j]);
        d[NLEN_256_28+i]+=carry;
    }
    BIG_256_28_sducopy(a,d);
    BIG_256_28_norm(a);

#endif

#ifdef DEBUG_NORM
    a[MPV_256_28]=1;
    a[MNV_256_28]=0;
#endif
}

/* General shift left of a by n bits */
/* a MUST be normalised */
/* SU= 32 */
void BIG_256_28_shl(BIG_256_28 a,int k)
{
    int i;
    int n=k%BASEBITS_256_28;
    int m=k/BASEBITS_256_28;

    a[NLEN_256_28-1]=((a[NLEN_256_28-1-m]<<n));
    if (NLEN_256_28>=m+2) a[NLEN_256_28-1]|=(a[NLEN_256_28-m-2]>>(BASEBITS_256_28-n));

    for (i=NLEN_256_28-2; i>m; i--)
        a[i]=((a[i-m]<<n)&BMASK_256_28)|(a[i-m-1]>>(BASEBITS_256_28-n));
    a[m]=(a[0]<<n)&BMASK_256_28;
    for (i=0; i<m; i++) a[i]=0;

}

/* Fast shift left of a by n bits, where n less than a word, Return excess (but store it as well) */
/* a MUST be normalised */
/* SU= 16 */
int BIG_256_28_fshl(BIG_256_28 a,int n)
{
    int i;

    a[NLEN_256_28-1]=((a[NLEN_256_28-1]<<n))|(a[NLEN_256_28-2]>>(BASEBITS_256_28-n)); /* top word not masked */
    for (i=NLEN_256_28-2; i>0; i--)
        a[i]=((a[i]<<n)&BMASK_256_28)|(a[i-1]>>(BASEBITS_256_28-n));
    a[0]=(a[0]<<n)&BMASK_256_28;

    return (int)(a[NLEN_256_28-1]>>((8*MODBYTES_256_28)%BASEBITS_256_28)); /* return excess - only used in ff.c */
}

/* double length left shift of a by k bits - k can be > BASEBITS , a MUST be normalised */
/* SU= 32 */
void BIG_256_28_dshl(DBIG_256_28 a,int k)
{
    int i;
    int n=k%BASEBITS_256_28;
    int m=k/BASEBITS_256_28;

    a[DNLEN_256_28-1]=((a[DNLEN_256_28-1-m]<<n))|(a[DNLEN_256_28-m-2]>>(BASEBITS_256_28-n));

    for (i=DNLEN_256_28-2; i>m; i--)
        a[i]=((a[i-m]<<n)&BMASK_256_28)|(a[i-m-1]>>(BASEBITS_256_28-n));
    a[m]=(a[0]<<n)&BMASK_256_28;
    for (i=0; i<m; i++) a[i]=0;

}

/* General shift right of a by k bits */
/* a MUST be normalised */
/* SU= 32 */
void BIG_256_28_shr(BIG_256_28 a,int k)
{
    int i;
    int n=k%BASEBITS_256_28;
    int m=k/BASEBITS_256_28;
    for (i=0; i<NLEN_256_28-m-1; i++)
        a[i]=(a[m+i]>>n)|((a[m+i+1]<<(BASEBITS_256_28-n))&BMASK_256_28);
    if (NLEN_256_28>m)  a[NLEN_256_28-m-1]=a[NLEN_256_28-1]>>n;
    for (i=NLEN_256_28-m; i<NLEN_256_28; i++) a[i]=0;

}

/* Fast combined shift, subtract and norm. Return sign of result */
int BIG_256_28_ssn(BIG_256_28 r,BIG_256_28 a,BIG_256_28 m)
{
    int i,n=NLEN_256_28-1;
    chunk carry;
    m[0]=(m[0]>>1)|((m[1]<<(BASEBITS_256_28-1))&BMASK_256_28);
    r[0]=a[0]-m[0];
    carry=r[0]>>BASEBITS_256_28;
    r[0]&=BMASK_256_28;

    for (i=1; i<n; i++)
    {
        m[i]=(m[i]>>1)|((m[i+1]<<(BASEBITS_256_28-1))&BMASK_256_28);
        r[i]=a[i]-m[i]+carry;
        carry=r[i]>>BASEBITS_256_28;
        r[i]&=BMASK_256_28;
    }

    m[n]>>=1;
    r[n]=a[n]-m[n]+carry;
#ifdef DEBUG_NORM
    r[MPV_256_28]=1;
    r[MNV_256_28]=0;
#endif
    return ((r[n]>>(CHUNK-1))&1);
}

/* Faster shift right of a by k bits. Return shifted out part */
/* a MUST be normalised */
/* SU= 16 */
int BIG_256_28_fshr(BIG_256_28 a,int k)
{
    int i;
    chunk r=a[0]&(((chunk)1<<k)-1); /* shifted out part */
    for (i=0; i<NLEN_256_28-1; i++)
        a[i]=(a[i]>>k)|((a[i+1]<<(BASEBITS_256_28-k))&BMASK_256_28);
    a[NLEN_256_28-1]=a[NLEN_256_28-1]>>k;
    return (int)r;
}

/* double length right shift of a by k bits - can be > BASEBITS */
/* SU= 32 */
void BIG_256_28_dshr(DBIG_256_28 a,int k)
{
    int i;
    int n=k%BASEBITS_256_28;
    int m=k/BASEBITS_256_28;
    for (i=0; i<DNLEN_256_28-m-1; i++)
        a[i]=(a[m+i]>>n)|((a[m+i+1]<<(BASEBITS_256_28-n))&BMASK_256_28);
    a[DNLEN_256_28-m-1]=a[DNLEN_256_28-1]>>n;
    for (i=DNLEN_256_28-m; i<DNLEN_256_28; i++ ) a[i]=0;
}

/* Split DBIG d into two BIGs t|b. Split happens at n bits, where n falls into NLEN word */
/* d MUST be normalised */
/* SU= 24 */
chunk BIG_256_28_split(BIG_256_28 t,BIG_256_28 b,DBIG_256_28 d,int n)
{
    int i;
    chunk nw,carry=0;
    int m=n%BASEBITS_256_28;

    if (m==0)
    {
        for (i=0; i<NLEN_256_28; i++) b[i]=d[i];
        if (t!=b)
        {
            for (i=NLEN_256_28; i<2*NLEN_256_28; i++) t[i-NLEN_256_28]=d[i];
            carry=t[NLEN_256_28-1]>>BASEBITS_256_28;
            t[NLEN_256_28-1]=t[NLEN_256_28-1]&BMASK_256_28; /* top word normalized */
        }
        return carry;
    }

    for (i=0; i<NLEN_256_28-1; i++) b[i]=d[i];

    b[NLEN_256_28-1]=d[NLEN_256_28-1]&(((chunk)1<<m)-1);

    if (t!=b)
    {
        carry=(d[DNLEN_256_28-1]<<(BASEBITS_256_28-m));
        for (i=DNLEN_256_28-2; i>=NLEN_256_28-1; i--)
        {
            nw=(d[i]>>m)|carry;
            carry=(d[i]<<(BASEBITS_256_28-m))&BMASK_256_28;
            t[i-NLEN_256_28+1]=nw;
        }
    }
#ifdef DEBUG_NORM
    t[MPV_256_28]=1;
    t[MNV_256_28]=0;
    b[MPV_256_28]=1;
    b[MNV_256_28]=0;
#endif
    return carry;
}

/* you gotta keep the sign of carry! Look - no branching! */
/* Note that sign bit is needed to disambiguate between +ve and -ve values */
/* normalise BIG - force all digits < 2^BASEBITS */
chunk BIG_256_28_norm(BIG_256_28 a)
{
    int i;
    chunk d,carry=0;
    for (i=0; i<NLEN_256_28-1; i++)
    {
        d=a[i]+carry;
        a[i]=d&BMASK_256_28;
        carry=d>>BASEBITS_256_28;
    }
    a[NLEN_256_28-1]=(a[NLEN_256_28-1]+carry);

#ifdef DEBUG_NORM
    a[MPV_256_28]=1;
    a[MNV_256_28]=0;
#endif
    return (a[NLEN_256_28-1]>>((8*MODBYTES_256_28)%BASEBITS_256_28));  /* only used in ff.c */
}

void BIG_256_28_dnorm(DBIG_256_28 a)
{
    int i;
    chunk d,carry=0;
    for (i=0; i<DNLEN_256_28-1; i++)
    {
        d=a[i]+carry;
        a[i]=d&BMASK_256_28;
        carry=d>>BASEBITS_256_28;
    }
    a[DNLEN_256_28-1]=(a[DNLEN_256_28-1]+carry);
#ifdef DEBUG_NORM
    a[DMPV_256_28]=1;
    a[DMNV_256_28]=0;
#endif
}

/* Compare a and b. Return 1 for a>b, -1 for a<b, 0 for a==b */
/* a and b MUST be normalised before call */
int BIG_256_28_comp(BIG_256_28 a,BIG_256_28 b)
{
    int i;
    for (i=NLEN_256_28-1; i>=0; i--)
    {
        if (a[i]==b[i]) continue;
        if (a[i]>b[i]) return 1;
        else  return -1;
    }
    return 0;
}

int BIG_256_28_dcomp(DBIG_256_28 a,DBIG_256_28 b)
{
    int i;
    for (i=DNLEN_256_28-1; i>=0; i--)
    {
        if (a[i]==b[i]) continue;
        if (a[i]>b[i]) return 1;
        else  return -1;
    }
    return 0;
}

/* return number of bits in a */
/* SU= 8 */
int BIG_256_28_nbits(BIG_256_28 a)
{
    int bts,k=NLEN_256_28-1;
    BIG_256_28 t;
    chunk c;
    BIG_256_28_copy(t,a);
    BIG_256_28_norm(t);
    while (k>=0 && t[k]==0) k--;
    if (k<0) return 0;
    bts=BASEBITS_256_28*k;
    c=t[k];
    while (c!=0)
    {
        c/=2;
        bts++;
    }
    return bts;
}

/* SU= 8, Calculate number of bits in a DBIG - output normalised */
int BIG_256_28_dnbits(DBIG_256_28 a)
{
    int bts,k=DNLEN_256_28-1;
    DBIG_256_28 t;
    chunk c;
    BIG_256_28_dcopy(t,a);
    BIG_256_28_dnorm(t);
    while (k>=0 && t[k]==0) k--;
    if (k<0) return 0;
    bts=BASEBITS_256_28*k;
    c=t[k];
    while (c!=0)
    {
        c/=2;
        bts++;
    }
    return bts;
}


/* Set b=b mod c */
/* SU= 16 */
void BIG_256_28_mod(BIG_256_28 b,BIG_256_28 c1)
{
    int k=0;
    BIG_256_28 r; /**/
    BIG_256_28 c;
    BIG_256_28_copy(c,c1);

    BIG_256_28_norm(b);
    if (BIG_256_28_comp(b,c)<0)
        return;
    do
    {
        BIG_256_28_fshl(c,1);
        k++;
    }
    while (BIG_256_28_comp(b,c)>=0);

    while (k>0)
    {
        BIG_256_28_fshr(c,1);

// constant time...
        BIG_256_28_sub(r,b,c);
        BIG_256_28_norm(r);
        BIG_256_28_cmove(b,r,1-((r[NLEN_256_28-1]>>(CHUNK-1))&1));
        k--;
    }
}

/* Set a=b mod c, b is destroyed. Slow but rarely used. */
/* SU= 96 */
void BIG_256_28_dmod(BIG_256_28 a,DBIG_256_28 b,BIG_256_28 c)
{
    int k=0;
    DBIG_256_28 m,r;
    BIG_256_28_dnorm(b);
    BIG_256_28_dscopy(m,c);

    if (BIG_256_28_dcomp(b,m)<0)
    {
        BIG_256_28_sdcopy(a,b);
        return;
    }

    do
    {
        BIG_256_28_dshl(m,1);
        k++;
    }
    while (BIG_256_28_dcomp(b,m)>=0);

    while (k>0)
    {
        BIG_256_28_dshr(m,1);
// constant time...
        BIG_256_28_dsub(r,b,m);
        BIG_256_28_dnorm(r);
        BIG_256_28_dcmove(b,r,1-((r[DNLEN_256_28-1]>>(CHUNK-1))&1));

        k--;
    }
    BIG_256_28_sdcopy(a,b);
}

/* Set a=b/c,  b is destroyed. Slow but rarely used. */
/* SU= 136 */

void BIG_256_28_ddiv(BIG_256_28 a,DBIG_256_28 b,BIG_256_28 c)
{
    int d,k=0;
    DBIG_256_28 m,dr;
    BIG_256_28 e,r;
    BIG_256_28_dnorm(b);
    BIG_256_28_dscopy(m,c);

    BIG_256_28_zero(a);
    BIG_256_28_zero(e);
    BIG_256_28_inc(e,1);

    while (BIG_256_28_dcomp(b,m)>=0)
    {
        BIG_256_28_fshl(e,1);
        BIG_256_28_dshl(m,1);
        k++;
    }

    while (k>0)
    {
        BIG_256_28_dshr(m,1);
        BIG_256_28_fshr(e,1);

        BIG_256_28_dsub(dr,b,m);
        BIG_256_28_dnorm(dr);
        d=1-((dr[DNLEN_256_28-1]>>(CHUNK-1))&1);
        BIG_256_28_dcmove(b,dr,d);

        BIG_256_28_add(r,a,e);
        BIG_256_28_norm(r);
        BIG_256_28_cmove(a,r,d);

        k--;
    }
}

/* SU= 136 */

void BIG_256_28_sdiv(BIG_256_28 a,BIG_256_28 c)
{
    int d,k=0;
    BIG_256_28 m,e,b,r;
    BIG_256_28_norm(a);
    BIG_256_28_copy(b,a);
    BIG_256_28_copy(m,c);

    BIG_256_28_zero(a);
    BIG_256_28_zero(e);
    BIG_256_28_inc(e,1);

    while (BIG_256_28_comp(b,m)>=0)
    {
        BIG_256_28_fshl(e,1);
        BIG_256_28_fshl(m,1);
        k++;
    }

    while (k>0)
    {
        BIG_256_28_fshr(m,1);
        BIG_256_28_fshr(e,1);

        BIG_256_28_sub(r,b,m);
        BIG_256_28_norm(r);
        d=1-((r[NLEN_256_28-1]>>(CHUNK-1))&1);
        BIG_256_28_cmove(b,r,d);

        BIG_256_28_add(r,a,e);
        BIG_256_28_norm(r);
        BIG_256_28_cmove(a,r,d);
        k--;
    }
}

/* return LSB of a */
int BIG_256_28_parity(BIG_256_28 a)
{
    return a[0]%2;
}

/* return n-th bit of a */
/* SU= 16 */
int BIG_256_28_bit(BIG_256_28 a,int n)
{
    if (a[n/BASEBITS_256_28]&((chunk)1<<(n%BASEBITS_256_28))) return 1;
    else return 0;
}

/* return last n bits of a, where n is small < BASEBITS */
/* SU= 16 */
int BIG_256_28_lastbits(BIG_256_28 a,int n)
{
    int msk=(1<<n)-1;
    BIG_256_28_norm(a);
    return ((int)a[0])&msk;
}

/* get 8*MODBYTES size random number */
void BIG_256_28_random(BIG_256_28 m,csprng *rng)
{
    int i,b,j=0,r=0;
    int len=8*MODBYTES_256_28;

    BIG_256_28_zero(m);
    /* generate random BIG */
    for (i=0; i<len; i++)
    {
        if (j==0) r=RAND_byte(rng);
        else r>>=1;
        b=r&1;
        BIG_256_28_shl(m,1);
        m[0]+=b;
        j++;
        j&=7;
    }

#ifdef DEBUG_NORM
    m[MPV_256_28]=1;
    m[MNV_256_28]=0;
#endif
}

/* get random BIG from rng, modulo q. Done one bit at a time, so its portable */

void BIG_256_28_randomnum(BIG_256_28 m,BIG_256_28 q,csprng *rng)
{
    int i,b,j=0,r=0;
    DBIG_256_28 d;
    BIG_256_28_dzero(d);
    /* generate random DBIG */
    for (i=0; i<2*BIG_256_28_nbits(q); i++)
    {
        if (j==0) r=RAND_byte(rng);
        else r>>=1;
        b=r&1;
        BIG_256_28_dshl(d,1);
        d[0]+=b;
        j++;
        j&=7;
    }
    /* reduce modulo a BIG. Removes bias */
    BIG_256_28_dmod(m,d,q);
#ifdef DEBUG_NORM
    m[MPV_256_28]=1;
    m[MNV_256_28]=0;
#endif
}

/* Set r=a*b mod m */
/* SU= 96 */
void BIG_256_28_modmul(BIG_256_28 r,BIG_256_28 a1,BIG_256_28 b1,BIG_256_28 m)
{
    DBIG_256_28 d;
    BIG_256_28 a,b;
    BIG_256_28_copy(a,a1);
    BIG_256_28_copy(b,b1);
    BIG_256_28_mod(a,m);
    BIG_256_28_mod(b,m);

    BIG_256_28_mul(d,a,b);
    BIG_256_28_dmod(r,d,m);
}

/* Set a=a*a mod m */
/* SU= 88 */
void BIG_256_28_modsqr(BIG_256_28 r,BIG_256_28 a1,BIG_256_28 m)
{
    DBIG_256_28 d;
    BIG_256_28 a;
    BIG_256_28_copy(a,a1);
    BIG_256_28_mod(a,m);
    BIG_256_28_sqr(d,a);
    BIG_256_28_dmod(r,d,m);
}

/* Set r=-a mod m */
/* SU= 16 */
void BIG_256_28_modneg(BIG_256_28 r,BIG_256_28 a1,BIG_256_28 m)
{
    BIG_256_28 a;
    BIG_256_28_copy(a,a1);
    BIG_256_28_mod(a,m);
    BIG_256_28_sub(r,m,a);
}

/* Set a=a/b mod m */
/* SU= 136 */
void BIG_256_28_moddiv(BIG_256_28 r,BIG_256_28 a1,BIG_256_28 b1,BIG_256_28 m)
{
    DBIG_256_28 d;
    BIG_256_28 z;
    BIG_256_28 a,b;
    BIG_256_28_copy(a,a1);
    BIG_256_28_copy(b,b1);

    BIG_256_28_mod(a,m);
    BIG_256_28_invmodp(z,b,m);

    BIG_256_28_mul(d,a,z);
    BIG_256_28_dmod(r,d,m);
}

/* Get jacobi Symbol (a/p). Returns 0, 1 or -1 */
/* SU= 216 */
int BIG_256_28_jacobi(BIG_256_28 a,BIG_256_28 p)
{
    int n8,k,m=0;
    BIG_256_28 t,x,n,zilch,one;
    BIG_256_28_one(one);
    BIG_256_28_zero(zilch);
    if (BIG_256_28_parity(p)==0 || BIG_256_28_comp(a,zilch)==0 || BIG_256_28_comp(p,one)<=0) return 0;
    BIG_256_28_norm(a);
    BIG_256_28_copy(x,a);
    BIG_256_28_copy(n,p);
    BIG_256_28_mod(x,p);

    while (BIG_256_28_comp(n,one)>0)
    {
        if (BIG_256_28_comp(x,zilch)==0) return 0;
        n8=BIG_256_28_lastbits(n,3);
        k=0;
        while (BIG_256_28_parity(x)==0)
        {
            k++;
            BIG_256_28_shr(x,1);
        }
        if (k%2==1) m+=(n8*n8-1)/8;
        m+=(n8-1)*(BIG_256_28_lastbits(x,2)-1)/4;
        BIG_256_28_copy(t,n);

        BIG_256_28_mod(t,x);
        BIG_256_28_copy(n,x);
        BIG_256_28_copy(x,t);
        m%=2;

    }
    if (m==0) return 1;
    else return -1;
}

/* Arazi and Qi inversion mod 256 */
static int invmod256(int a)
{
    int U,t1,t2,b,c;
    t1=0;
    c=(a>>1)&1;
    t1+=c;
    t1&=1;
    t1=2-t1;
    t1<<=1;
    U=t1+1;

// i=2
    b=a&3;
    t1=U*b;
    t1>>=2;
    c=(a>>2)&3;
    t2=(U*c)&3;
    t1+=t2;
    t1*=U;
    t1&=3;
    t1=4-t1;
    t1<<=2;
    U+=t1;

// i=4
    b=a&15;
    t1=U*b;
    t1>>=4;
    c=(a>>4)&15;
    t2=(U*c)&15;
    t1+=t2;
    t1*=U;
    t1&=15;
    t1=16-t1;
    t1<<=4;
    U+=t1;

    return U;
}

/* a=1/a mod 2^BIGBITS. This is very fast! */
void BIG_256_28_invmod2m(BIG_256_28 a)
{
    int i;
    BIG_256_28 U,t1,b,c;
    BIG_256_28_zero(U);
    BIG_256_28_inc(U,invmod256(BIG_256_28_lastbits(a,8)));
    for (i=8; i<BIGBITS_256_28; i<<=1)
    {
        BIG_256_28_norm(U);
        BIG_256_28_copy(b,a);
        BIG_256_28_mod2m(b,i);   // bottom i bits of a

        BIG_256_28_smul(t1,U,b);
        BIG_256_28_shr(t1,i); // top i bits of U*b

        BIG_256_28_copy(c,a);
        BIG_256_28_shr(c,i);
        BIG_256_28_mod2m(c,i); // top i bits of a

        BIG_256_28_smul(b,U,c);
        BIG_256_28_mod2m(b,i);  // bottom i bits of U*c

        BIG_256_28_add(t1,t1,b);
        BIG_256_28_norm(t1);
        BIG_256_28_smul(b,t1,U);
        BIG_256_28_copy(t1,b);  // (t1+b)*U
        BIG_256_28_mod2m(t1,i);				// bottom i bits of (t1+b)*U

        BIG_256_28_one(b);
        BIG_256_28_shl(b,i);
        BIG_256_28_sub(t1,b,t1);
        BIG_256_28_norm(t1);

        BIG_256_28_shl(t1,i);

        BIG_256_28_add(U,U,t1);
    }
    BIG_256_28_copy(a,U);
    BIG_256_28_norm(a);
    BIG_256_28_mod2m(a,BIGBITS_256_28);
}

/* Set r=1/a mod p. Binary method */
/* SU= 240 */
void BIG_256_28_invmodp(BIG_256_28 r,BIG_256_28 a,BIG_256_28 p)
{
    BIG_256_28 u,v,x1,x2,t,one;
    BIG_256_28_mod(a,p);
    BIG_256_28_copy(u,a);
    BIG_256_28_copy(v,p);
    BIG_256_28_one(one);
    BIG_256_28_copy(x1,one);
    BIG_256_28_zero(x2);

    while (BIG_256_28_comp(u,one)!=0 && BIG_256_28_comp(v,one)!=0)
    {
        while (BIG_256_28_parity(u)==0)
        {
            BIG_256_28_fshr(u,1);
            if (BIG_256_28_parity(x1)!=0)
            {
                BIG_256_28_add(x1,p,x1);
                BIG_256_28_norm(x1);
            }
            BIG_256_28_fshr(x1,1);
        }
        while (BIG_256_28_parity(v)==0)
        {
            BIG_256_28_fshr(v,1);
            if (BIG_256_28_parity(x2)!=0)
            {
                BIG_256_28_add(x2,p,x2);
                BIG_256_28_norm(x2);
            }
            BIG_256_28_fshr(x2,1);
        }
        if (BIG_256_28_comp(u,v)>=0)
        {
            BIG_256_28_sub(u,u,v);
            BIG_256_28_norm(u);
            if (BIG_256_28_comp(x1,x2)>=0) BIG_256_28_sub(x1,x1,x2);
            else
            {
                BIG_256_28_sub(t,p,x2);
                BIG_256_28_add(x1,x1,t);
            }
            BIG_256_28_norm(x1);
        }
        else
        {
            BIG_256_28_sub(v,v,u);
            BIG_256_28_norm(v);
            if (BIG_256_28_comp(x2,x1)>=0) BIG_256_28_sub(x2,x2,x1);
            else
            {
                BIG_256_28_sub(t,p,x1);
                BIG_256_28_add(x2,x2,t);
            }
            BIG_256_28_norm(x2);
        }
    }
    if (BIG_256_28_comp(u,one)==0)
        BIG_256_28_copy(r,x1);
    else
        BIG_256_28_copy(r,x2);
}

/* set x = x mod 2^m */
void BIG_256_28_mod2m(BIG_256_28 x,int m)
{
    int i,wd,bt;
    chunk msk;
    BIG_256_28_norm(x);

    wd=m/BASEBITS_256_28;
    bt=m%BASEBITS_256_28;
    msk=((chunk)1<<bt)-1;
    x[wd]&=msk;
    for (i=wd+1; i<NLEN_256_28; i++) x[i]=0;
}

/* set x = x mod 2^m */
void BIG_256_28_dmod2m(DBIG_256_28 x,int m)
{
    int i,wd,bt;
    chunk msk;
    BIG_256_28_norm(x);

    wd=m/BASEBITS_256_28;
    bt=m%BASEBITS_256_28;
    msk=((chunk)1<<bt)-1;
    x[wd]&=msk;
    for (i=wd+1; i<DNLEN_256_28; i++) x[i]=0;
}

// new
/* Convert to DBIG number from byte array of given length */
void BIG_256_28_dfromBytesLen(DBIG_256_28 a,char *b,int s)
{
    int i,len=s;
    BIG_256_28_dzero(a);

    for (i=0; i<len; i++)
    {
        BIG_256_28_dshl(a,8);
        a[0]+=(int)(unsigned char)b[i];
    }
#ifdef DEBUG_NORM
    a[DMPV_256_28]=1;
    a[DMNV_256_28]=0;
#endif
}
