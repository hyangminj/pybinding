#pragma once
#include <fmt/format.h>
#include <fmt/ostream.h>

// Forward declare Chrono for formatter specialization
namespace cpb { class Chrono; }

// fmt::formatter specialization for cpb::Chrono
// This enables direct formatting of Chrono objects in fmt::format
template <>
struct fmt::formatter<cpb::Chrono> : fmt::formatter<std::string> {
    auto format(const cpb::Chrono& c, fmt::format_context& ctx) const
        -> decltype(ctx.out());
};

// Compatibility: Provide _format user-defined literal that was removed in fmt 11.x
// This allows existing code using "..."_format(args...) to continue working
namespace cpb {
namespace fmt_literals {
    struct format_string_adapter {
        const char* str;
        constexpr format_string_adapter(const char* s) : str(s) {}

        template<typename... Args>
        std::string operator()(Args&&... args) const {
            return fmt::format(fmt::runtime(str), std::forward<Args>(args)...);
        }
    };

    constexpr format_string_adapter operator""_format(const char* s, std::size_t) {
        return format_string_adapter(s);
    }
} // namespace fmt_literals
} // namespace cpb

// Make _format available in the global namespace for backward compatibility
using cpb::fmt_literals::operator""_format;

namespace fmt {

/**
 Convert number to string with SI suffix, e.g.: 14226 -> 14.2k, 5395984 -> 5.39M
 */
inline std::string with_suffix(double number) {
    struct Pair {
        double value;
        char const* suffix;
    };
    static constexpr Pair mapping[] = {{1e9, "G"}, {1e6, "M"}, {1e3, "k"}};

    auto const result = [&]{
        for (auto const& bucket : mapping) {
            if (number > 0.999 * bucket.value) {
                return Pair{number / bucket.value, bucket.suffix};
            }
        }
        return Pair{number, ""};
    }();

    return fmt::format("{:.3g}{}", result.value, result.suffix);
}

inline std::string with_suffix(std::ptrdiff_t n) { return with_suffix(static_cast<double>(n)); }

} // namespace fmt
