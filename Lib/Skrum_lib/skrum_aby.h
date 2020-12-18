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
const uint32_t bitlen = 32;


void init_skrum_aby(std::string address, uint16_t port, bool role_is_server);

void shutdown_skrum_aby();

void reset_skrum_aby();


std::vector <uint32_t>
skrum_mul(bool role, std::vector <uint32_t> *d, std::vector <uint32_t> *sign, uint32_t length, uint32_t num_dis);

std::vector <uint32_t> skrum_secp(bool role, std::vector <uint32_t> *data, uint32_t length);

#endif
