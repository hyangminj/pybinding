#pragma once
#include <variant>
#include <complex>

namespace cpb { namespace var {

// Use std::variant instead of mapbox::variant for C++17
template<class... Types>
using variant = std::variant<Types...>;

template<class T, class... Types>
constexpr T& get(variant<Types...>& v) {
    return std::get<T>(v);
}

template<class T, class... Types>
constexpr const T& get(const variant<Types...>& v) {
    return std::get<T>(v);
}

template<class Visitor, class... Variants>
constexpr auto apply_visitor(Visitor&& vis, Variants&&... vars) {
    return std::visit(std::forward<Visitor>(vis), std::forward<Variants>(vars)...);
}

/// Variant of a container with real elements
template<template<class> class... C>
using real = variant<C<float>..., C<double>...>;

/// Variant of a container with real or complex elements
template<template<class> class... C>
using complex = variant<C<float>..., C<std::complex<float>>...,
                        C<double>..., C<std::complex<double>>...>;

template<class T> struct tag {};

using scalar_tag = complex<tag>;

}} // namespace cpb::var
