#pragma once
#include <memory>
#include <type_traits>
#include <utility>

// C++17 is now the minimum standard.
// This header provides backward-compatible aliases that map to std:: equivalents.
// Kept for source compatibility with existing code.

namespace cpb {

// Aliases mapping old std14:: names to standard library (available since C++14/C++17)
namespace std14 {
    using std::make_unique;
    using std::cbegin;
    using std::cend;
    using std::enable_if_t;
    using std::conditional_t;
    using std::add_const_t;
    using std::remove_const_t;
    using std::remove_pointer_t;
    using std::decay_t;
} // namespace std14

// Aliases mapping old std17:: names to standard library (available since C++17)
namespace std17 {
    using std::as_const;
} // namespace std17

} // namespace cpb
