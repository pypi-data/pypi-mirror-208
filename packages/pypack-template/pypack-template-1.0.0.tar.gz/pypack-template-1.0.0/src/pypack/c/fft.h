#include <vector>
#include <string>
#include <iostream>
#include <complex>

using namespace std;

void __print(int x) {cerr << x;}
void __print(long x) {cerr << x;}
void __print(long long x) {cerr << x;}
void __print(unsigned x) {cerr << x;}
void __print(unsigned long x) {cerr << x;}
void __print(unsigned long long x) {cerr << x;}
void __print(float x) {cerr << x;}
void __print(double x) {cerr << x;}
void __print(long double x) {cerr << x;}
void __print(char x) {cerr << '\'' << x << '\'';}
void __print(const char *x) {cerr << '\"' << x << '\"';}
void __print(const string &x) {cerr << '\"' << x << '\"';}
void __print(bool x) {cerr << (x ? "true" : "false");}

template<typename T, typename V>
void __print(const pair<T, V> &x) {cerr << '{'; __print(x.first); cerr << ','; __print(x.second); cerr << '}';}
template<typename T>
void __print(const complex<T> &x) {__print(x.real()); cerr << '+'; __print(x.imag()); cerr << 'i';}
template<typename T>
void __print(const T &x) {int f = 0; cerr << '{'; for (auto &i: x) cerr << (f++ ? "," : ""), __print(i); cerr << "}";}
void _print() {cerr << "]\n";}
template <typename T, typename... V>
void _print(T t, V... v) {__print(t); if (sizeof...(v)) cerr << ", "; _print(v...);}
#ifndef PROD
#define debug(x...) cerr << "[" << #x << "] = ["; _print(x)
#else
#define debug(x...)
#endif

typedef vector<complex<double>> type_vcd;
typedef vector<double> type_vi;

type_vcd fft(type_vcd const & p) {
    int n = p.size();
    if (n <= 1)
        return {p[0]};
    type_vcd temp(n / 2);
    for (int i = 0; i < n / 2; ++i) temp[i] = p[i * 2];
    auto fftl = fft(temp);
    for (int i = 0; i < n / 2; ++i) temp[i] = p[i * 2 + 1];
    auto fftr = fft(temp);
    type_vcd res(n);
    for (int i = 0; i < n; ++i) {
        auto theta = -2 * 3.1415926 * i / n;
        complex<double> root(cos(theta), sin(theta));
        res[i] = fftl[i % (n / 2)] + root * fftr[i % (n / 2)];
    }
    return res;
}

type_vcd ifft(type_vcd & p) {
    // reverse(p.begin(), p.end());
    for (auto& x: p) x = conj(x);
    auto res = fft(p);
    for (auto & x: res) x = conj(x) / double(p.size());
    return res;
}

type_vi convolution(type_vi const& a, type_vi const& b) {
    int n_real = a.size() + b.size() - 1;
    int n = 1;
    while (n < n_real) n <<= 1;
    auto trans = [](type_vi const& p, int n) {
        type_vcd res(n, complex<double>());
        for (int i = 0; i < p.size(); ++i) res[i] = complex<double>(p[i]);
        return res;
    };
    auto pa = trans(a, n);
    auto pb = trans(b, n);
    debug(pa, pb);
    auto ffta = fft(pa);
    auto fftb = fft(pb);
    debug(ffta, fftb);
    for (int i = 0; i < n; ++i) {
        ffta[i] *= fftb[i];
    }
    debug(ffta);
    fftb = ifft(ffta);
    debug(fftb);
    type_vi res(n_real, 3);
    for (int i = 0; i < n_real; ++i) {
        res[i] = fftb[i].real();
    }
    return res;
}