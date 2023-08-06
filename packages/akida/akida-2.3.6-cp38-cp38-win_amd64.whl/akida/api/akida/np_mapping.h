#pragma once

#include <algorithm>
#include <map>
#include <vector>

#include "akida/np.h"
#include "akida/shape.h"

namespace akida {

struct NPSpace {
  Index x;
  Index y;
  Shape shape;
};

struct NPMapping {
  NPMapping(np::Type np_type, const NPSpace& in_int, const NPSpace& in_aug,
            Index start_n, Index neurons, bool single_buf,
            np::Ident np_id = np::HRC_IDENT)
      : np(np_id),
        type(np_type),
        start_neuron(start_n),
        num_neurons(neurons),
        input_int(in_int),
        input_aug(in_aug),
        single_buffer(single_buf) {}
  NPMapping(np::Type np_type, const Shape& shape, Index start_n, Index neurons,
            bool single_buf, np::Ident np_id = np::HRC_IDENT)
      : np(np_id),
        type(np_type),
        start_neuron(start_n),
        num_neurons(neurons),
        input_int{0, 0, shape},
        input_aug{0, 0, shape},
        single_buffer(single_buf) {}
  explicit NPMapping(np::Ident np_id)
      : NPMapping(np::Type::HRC, {}, 0, 0, false, np_id) {}
  np::Ident np;
  np::Type type;
  Index start_neuron;
  Index num_neurons;
  // Internal input box
  NPSpace input_int;
  // Augmented input box
  NPSpace input_aug;
  // Use single buffer or dual ping-pong buffer
  bool single_buffer;
};

// utility function to find the leftmost or rightmost NPs
inline uint8_t find_border_column(const std::vector<NPMapping>& nps,
                                  bool find_left) {
  auto border_np = *std::min_element(
      nps.begin(), nps.end(),
      [find_left](const NPMapping& left, const NPMapping& right) {
        return find_left ? left.np.col < right.np.col
                         : left.np.col > right.np.col;
      });
  return border_np.np.col;
}

}  // namespace akida
