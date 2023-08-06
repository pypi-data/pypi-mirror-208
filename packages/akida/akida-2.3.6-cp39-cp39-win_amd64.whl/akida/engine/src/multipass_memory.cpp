#include "multipass_memory.h"

#include "dma_desc_format.h"
#include "memory_mgr.h"
#include "program_play.h"

namespace akida {

void MultiPassMemory::alloc_memory(MemoryMgr* memory_mgr,
                                   const uint8_t* program) {
  dummy_output_addr = memory_mgr->alloc(sizeof(dma::w32));
  // descriptor size depend on input DMA used
  const auto descriptor_size = program::input_is_dense(program)
                                   ? dma::hrc::DESC_BYTE_SIZE
                                   : dma::event::DESC_BYTE_SIZE;
  hw_generated_descriptor_addr = memory_mgr->alloc(descriptor_size);
  hw_generated_descriptor_out_addr = memory_mgr->alloc(sizeof(dma::w32));
}

void MultiPassMemory::free_memory(MemoryMgr* memory_mgr) {
  // we need to free dummy output
  memory_mgr->free(dummy_output_addr);
  // we need to free HW generated descriptor
  memory_mgr->free(hw_generated_descriptor_addr);
  // we need to free replay OB payload
  memory_mgr->free(hw_generated_descriptor_out_addr);
}

void MultiPassMemory::update_learn_descriptor_addr(
    dma::addr learn_descriptor_address) {
  learn_descriptor_addr = learn_descriptor_address;
}

}  // namespace akida
