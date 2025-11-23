#pragma once
#include <variant>
#include <complex>

namespace cpb { namespace var {

// A wrapper around std::variant to provide an API compatible with mapbox::variant
template<class... Types>
class variant {
    std::variant<Types...> impl;

public:
    // Inherit constructors from std::variant
    template<typename... Args>
    variant(Args&&... args) : impl(std::forward<Args>(args)...) {}

    // Default constructor
    variant() = default;

    // Copy and move
    variant(const variant&) = default;
    variant(variant&&) = default;
    variant& operator=(const variant&) = default;
    variant& operator=(variant&&) = default;

    // Assignment from underlying types
    template<class T>
    variant& operator=(T&& t) {
        impl = std::forward<T>(t);
        return *this;
    }

    // Check if the variant holds a specific type (mapbox::variant API)
    template<class T>
    bool is() const noexcept {
        return std::holds_alternative<T>(impl);
    }

    // Get the value of a specific type (mapbox::variant API)
    template<class T>
    T& get() {
        return std::get<T>(impl);
    }

    template<class T>
    const T& get() const {
        return std::get<T>(impl);
    }

    // Apply a visitor (equivalent to mapbox::variant::match)
    template<class Visitor>
    auto match(Visitor&& vis) {
        return std::visit(std::forward<Visitor>(vis), impl);
    }

    template<class Visitor>
    auto match(Visitor&& vis) const {
        return std::visit(std::forward<Visitor>(vis), impl);
    }

    // Access to underlying std::variant for std::get/std::visit
    std::variant<Types...>& get_variant() { return impl; }
    const std::variant<Types...>& get_variant() const { return impl; }
};

// Free function versions for compatibility
template<class T, class... Types>
constexpr T& get(variant<Types...>& v) {
    return v.template get<T>();
}

template<class T, class... Types>
constexpr const T& get(const variant<Types...>& v) {
    return v.template get<T>();
}

template<class Visitor, class... Variants>
constexpr auto apply_visitor(Visitor&& vis, Variants&&... vars) {
    return std::visit(std::forward<Visitor>(vis), std::forward<Variants>(vars).get_variant()...);
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
