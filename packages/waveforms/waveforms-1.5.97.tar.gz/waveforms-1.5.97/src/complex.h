#ifndef COMPLEX_H
#define COMPLEX_H

#include <stdint.h>

static inline void complex_add_int8(int8_t *r1, int8_t *i1, int8_t r2, int8_t i2)
{
    *r1 += r2;
    *i1 += i2;
}

static inline void complex_sub_int8(int8_t *r1, int8_t *i1, int8_t r2, int8_t i2)
{
    *r1 -= r2;
    *i1 -= i2;
}

static inline void complex_mul_int8(int8_t *r1, int8_t *i1, int8_t r2, int8_t i2)
{
    int8_t r = *r1 * r2 - *i1 * i2;
    *r1 = r;
    *i1 = *r1 * i2 + *i1 * r2;
}

static inline void complex_div_int8(int8_t *r1, int8_t *i1, int8_t r2, int8_t i2)
{
    int8_t r = (*r1 * r2 + *i1 * i2) / (r2 * r2 + i2 * i2);
    *r1 = r;
    *i1 = (*i1 * r2 - *r1 * i2) / (r2 * r2 + i2 * i2);
}

static inline void complex_add_int16(int16_t *r1, int16_t *i1, int16_t r2, int16_t i2)
{
    *r1 += r2;
    *i1 += i2;
}

static inline void complex_sub_int16(int16_t *r1, int16_t *i1, int16_t r2, int16_t i2)
{
    *r1 -= r2;
    *i1 -= i2;
}

static inline void complex_mul_int16(int16_t *r1, int16_t *i1, int16_t r2, int16_t i2)
{
    int16_t r = *r1 * r2 - *i1 * i2;
    *r1 = r;
    *i1 = *r1 * i2 + *i1 * r2;
}

static inline void complex_div_int16(int16_t *r1, int16_t *i1, int16_t r2, int16_t i2)
{
    int16_t r = (*r1 * r2 + *i1 * i2) / (r2 * r2 + i2 * i2);
    *r1 = r;
    *i1 = (*i1 * r2 - *r1 * i2) / (r2 * r2 + i2 * i2);
}

static inline void complex_add_int32(int32_t *r1, int32_t *i1, int32_t r2, int32_t i2)
{
    *r1 += r2;
    *i1 += i2;
}

static inline void complex_sub_int32(int32_t *r1, int32_t *i1, int32_t r2, int32_t i2)
{
    *r1 -= r2;
    *i1 -= i2;
}

static inline void complex_mul_int32(int32_t *r1, int32_t *i1, int32_t r2, int32_t i2)
{
    int32_t r = *r1 * r2 - *i1 * i2;
    *r1 = r;
    *i1 = *r1 * i2 + *i1 * r2;
}

static inline void complex_div_int32(int32_t *r1, int32_t *i1, int32_t r2, int32_t i2)
{
    int32_t r = (*r1 * r2 + *i1 * i2) / (r2 * r2 + i2 * i2);
    *r1 = r;
    *i1 = (*i1 * r2 - *r1 * i2) / (r2 * r2 + i2 * i2);
}

static inline void complex_add_int64(int64_t *r1, int64_t *i1, int64_t r2, int64_t i2)
{
    *r1 += r2;
    *i1 += i2;
}

static inline void complex_sub_int64(int64_t *r1, int64_t *i1, int64_t r2, int64_t i2)
{
    *r1 -= r2;
    *i1 -= i2;
}

static inline void complex_mul_int64(int64_t *r1, int64_t *i1, int64_t r2, int64_t i2)
{
    int64_t r = *r1 * r2 - *i1 * i2;
    *r1 = r;
    *i1 = *r1 * i2 + *i1 * r2;
}

static inline void complex_div_int64(int64_t *r1, int64_t *i1, int64_t r2, int64_t i2)
{
    int64_t r = (*r1 * r2 + *i1 * i2) / (r2 * r2 + i2 * i2);
    *r1 = r;
    *i1 = (*i1 * r2 - *r1 * i2) / (r2 * r2 + i2 * i2);
}

static inline void complex_add_float(float *r1, float *i1, float r2, float i2)
{
    *r1 += r2;
    *i1 += i2;
}

static inline void complex_sub_float(float *r1, float *i1, float r2, float i2)
{
    *r1 -= r2;
    *i1 -= i2;
}

static inline void complex_mul_float(float *r1, float *i1, float r2, float i2)
{
    float r = *r1 * r2 - *i1 * i2;
    *r1 = r;
    *i1 = *r1 * i2 + *i1 * r2;
}

static inline void complex_div_float(float *r1, float *i1, float r2, float i2)
{
    float r = (*r1 * r2 + *i1 * i2) / (r2 * r2 + i2 * i2);
    *r1 = r;
    *i1 = (*i1 * r2 - *r1 * i2) / (r2 * r2 + i2 * i2);
}

static inline void complex_add_double(double *r1, double *i1, double r2, double i2)
{
    *r1 += r2;
    *i1 += i2;
}

static inline void complex_sub_double(double *r1, double *i1, double r2, double i2)
{
    *r1 -= r2;
    *i1 -= i2;
}

static inline void complex_mul_double(double *r1, double *i1, double r2, double i2)
{
    double r = *r1 * r2 - *i1 * i2;
    *r1 = r;
    *i1 = *r1 * i2 + *i1 * r2;
}

static inline void complex_div_double(double *r1, double *i1, double r2, double i2)
{
    double r = (*r1 * r2 + *i1 * i2) / (r2 * r2 + i2 * i2);
    *r1 = r;
    *i1 = (*i1 * r2 - *r1 * i2) / (r2 * r2 + i2 * i2);
}

static inline void complex_add_long_double(long double *r1, long double *i1, long double r2, long double i2)
{
    *r1 += r2;
    *i1 += i2;
}

static inline void complex_sub_long_double(long double *r1, long double *i1, long double r2, long double i2)
{
    *r1 -= r2;
    *i1 -= i2;
}

static inline void complex_mul_long_double(long double *r1, long double *i1, long double r2, long double i2)
{
    long double r = *r1 * r2 - *i1 * i2;
    *r1 = r;
    *i1 = *r1 * i2 + *i1 * r2;
}

static inline void complex_div_long_double(long double *r1, long double *i1, long double r2, long double i2)
{
    long double r = (*r1 * r2 + *i1 * i2) / (r2 * r2 + i2 * i2);
    *r1 = r;
    *i1 = (*i1 * r2 - *r1 * i2) / (r2 * r2 + i2 * i2);
}

#endif // COMPLEX_H