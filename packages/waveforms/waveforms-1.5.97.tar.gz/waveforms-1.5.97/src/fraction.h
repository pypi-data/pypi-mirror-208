#ifndef FRACTION_H
#define FRACTION_H

#include <stdint.h>

typedef int32_t INT;

static inline INT gcd(INT a, INT b)
{
    int c;
    while (b != 0)
    {
        c = a % b;
        a = b;
        b = c;
    }
    return a;
}

static inline INT lcm(INT a, INT b)
{
    return a * b / gcd(a, b);
}

static inline void fraction_reduce(INT *n, INT *d)
{
    INT g = gcd(*n, *d);
    *n /= g;
    *d /= g;
}

static inline fraction_add(INT *n1, INT *d1, INT n2, INT d2)
{
    INT g = gcd(*d1, d2);
    *n1 = *n1 * (d2 / g) + n2 * (*d1 / g);
    *d1 = *d1 * (d2 / g);
}

static inline fraction_sub(INT *n1, INT *d1, INT n2, INT d2)
{
    INT g = gcd(*d1, d2);
    *n1 = *n1 * (d2 / g) - n2 * (*d1 / g);
    *d1 = *d1 * (d2 / g);
}

static inline fraction_mul(INT *n1, INT *d1, INT n2, INT d2)
{
    INT g1 = gcd(*n1, d2);
    INT g2 = gcd(*d1, n2);
    *n1 = (*n1 / g1) * (n2 / g2);
    *d1 = (*d1 / g2) * (d2 / g1);
}

static inline fraction_div(INT *n1, INT *d1, INT n2, INT d2)
{
    INT g1 = gcd(*n1, n2);
    INT g2 = gcd(*d1, d2);
    *n1 = (*n1 / g1) * (d2 / g2);
    *d1 = (*d1 / g2) * (n2 / g1);
}

#endif // FRACTION_H