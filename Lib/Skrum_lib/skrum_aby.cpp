#include "skrum_aby.h"


#include <vector>

ABYParty *skrum_party;


void init_skrum_aby(std::string address, uint16_t port, bool role_is_server) {
    e_role role;
    if (role_is_server) {
        role = (e_role) 0;
    } else {
        role = (e_role) 1;
    }

    skrum_party = new ABYParty(role, address, port, LT, bitlen, nthreads, mt_alg);
    std::cout << "init skrum success!" << std::endl;

}


void shutdown_skrum_aby() {
    delete skrum_party;
    std::cout << "shutdown skrum successs!" << std::endl;
}


void reset_skrum_aby() {
    skrum_party->Reset();
}


std::vector <uint32_t>
skrum_mul(bool role, std::vector <uint32_t> *d, std::vector <uint32_t> *sign, uint32_t length, uint32_t num_dis) {

    std::vector < Sharing * > &sharings = skrum_party->GetSharings();

    ArithmeticCircuit *ac = (ArithmeticCircuit *) sharings[S_ARITH]->GetCircuitBuildRoutine();
    BooleanCircuit *bc = (BooleanCircuit *) sharings[S_BOOL]->GetCircuitBuildRoutine();

    share **s_vec1 = (share **) malloc(sizeof(share *) * num_dis);
    share **s_vec2 = (share **) malloc(sizeof(share *) * num_dis);
    share **s_sign1 = (share **) malloc(sizeof(share *) * num_dis);
    share **s_sign2 = (share **) malloc(sizeof(share *) * num_dis);
    share **s_sign = (share **) malloc(sizeof(share *) * num_dis);
    share **s_mul = (share **) malloc(sizeof(share *) * num_dis);
    if (role) {
        for (int i = 0; i < num_dis; ++i) {
            s_vec1[i] = ac->PutSIMDINGate(length, d->data() + i * length, bitlen, SERVER);
            s_vec2[i] = ac->PutDummySIMDINGate(length, bitlen);
            s_sign1[i] = bc->PutSIMDINGate(length, sign->data() + i * length, bitlen, SERVER);
            s_sign2[i] = bc->PutDummySIMDINGate(length, bitlen);
        }
    } else {
        for (int i = 0; i < num_dis; ++i) {
            s_vec2[i] = ac->PutSIMDINGate(length, d->data() + i * length, bitlen, CLIENT);
            s_vec1[i] = ac->PutDummySIMDINGate(length, bitlen);
            s_sign2[i] = bc->PutSIMDINGate(length, sign->data() + i * length, bitlen, CLIENT);
            s_sign1[i] = bc->PutDummySIMDINGate(length, bitlen);
        }
    }

    uint32_t _two = 2;


    share **s_out = (share **) malloc(sizeof(share *) * 3 * num_dis);

    for (int i = 0; i < num_dis; ++i) {
        s_out[i] = ac->PutOUTGate(s_vec1[i], ALL);

        s_mul[i] = ac->PutMULGate(s_vec1[i], s_vec2[i]);

        s_out[i + num_dis] = ac->PutOUTGate(s_mul[i], ALL);

        s_sign[i] = bc->PutXORGate(s_sign1[i], s_sign2[i]);
        s_out[i + 2 * num_dis] = bc->PutOUTGate(s_sign[i], ALL);
    }

    skrum_party->ExecCircuit();

    std::vector <uint32_t> v_out;

    uint32_t *output;
    uint32_t out_bitlen, out_nvals;

    for (int i = 0; i < 3 * num_dis; i++) {
        s_out[i]->get_clear_value_vec(&output, &out_bitlen, &out_nvals);
        for (int j = 0; j < length; ++j) {
            v_out.push_back(output[j]);
        }
    }

    reset_skrum_aby();

    for (int i = 0; i < num_dis; ++i) {
        delete s_vec1[i];
        delete s_vec2[i];
        delete s_sign1[i];
        delete s_sign2[i];
        delete s_sign[i];
        delete s_mul[i];
        delete s_out[i];
    }
    delete s_vec1;
    delete s_vec2;
    delete s_sign1;
    delete s_sign2;
    delete s_sign;
    delete s_mul;
    delete s_out;

    return v_out;
}

std::vector <uint32_t>
skrum_secp(bool role, std::vector <uint32_t> *data, uint32_t length) {

    std::vector < Sharing * > &sharings = skrum_party->GetSharings();

    ArithmeticCircuit *ac = (ArithmeticCircuit *) sharings[S_ARITH]->GetCircuitBuildRoutine();

    share *s_data_x, *s_data_y;

    if (role) {
        s_data_x = ac->PutSIMDINGate(length, data->data(), bitlen, SERVER);
        s_data_y = ac->PutDummySIMDINGate(length, bitlen);
    } else {
        s_data_x = ac->PutDummySIMDINGate(length, bitlen);
        s_data_y = ac->PutSIMDINGate(length, data->data(), bitlen, CLIENT);
    }

    share *s_out = ac->PutOUTGate(s_data_x, ALL);

    skrum_party->ExecCircuit();

    std::vector <uint32_t> v_out;

    uint32_t *output;
    uint32_t out_bitlen, out_nvals;
    s_out->get_clear_value_vec(&output, &out_bitlen, &out_nvals);

    for (int i = 0; i < length; i++) {
        v_out.push_back(output[i]);
    }
    reset_skrum_aby();

    return v_out;
}
