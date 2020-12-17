#ifndef __KD_ABY_H__
#define __KD_ABY_H__

#include "../ABY/src/abycore/sharing/sharing.h"
#include "../ABY/src/abycore/circuit/booleancircuits.h"
#include "../ABY/src/abycore/circuit/arithmeticcircuits.h"
#include "../ABY/src/abycore/circuit/circuit.h"
#include "../ABY/src/abycore/aby/abyparty.h"

#include "../ABY/src/abycore/ABY_utils/ABYconstants.h"

#include <vector>


//for ABY
const uint32_t secparam = 128;
const uint32_t nthreads = 1;
const e_mt_gen_alg mt_alg = MT_OT;
const uint32_t bitlen = 8;
const uint32_t gbitlen = 32;


void init_sru_aby(std::string address, uint16_t port, bool role_is_server);
void init_kd_aby(std::string address, uint16_t port, bool role_is_server);
void shutdown_sru_aby();
void shutdown_kd_aby();

void reset_sru_aby();
void reset_kd_aby();

std::vector <uint8_t> kd_sru(bool role, std::vector <uint8_t> *idx, uint32_t num_workers, uint32_t length, int f);

share *
BuildSRUCircuit(share **s_xor, uint32_t num_workers, uint32_t f, uint32_t length, ArithmeticCircuit *ac,
                BooleanCircuit *bc,
                BooleanCircuit *yc);

std::vector <uint32_t>
kd_top(bool role, std::vector <uint32_t> *grad, std::vector <uint32_t> *fgrad, uint32_t k, uint32_t num_workers, uint32_t f);

share *BuildTOPCircuit(share **s_grad, share **s_fgrad, uint32_t num_workers, uint32_t f, ArithmeticCircuit *ac, BooleanCircuit *bc,
                       BooleanCircuit *yc);

#endif
