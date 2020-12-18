#include "kd_aby.h"


#include <vector>

ABYParty *sru_party;
ABYParty *kd_party;


void init_sru_aby(std::string address, uint16_t port, bool role_is_server) {
    e_role role;
    if (role_is_server) {
        role = (e_role) 0;
    } else {
        role = (e_role) 1;
    }

    sru_party = new ABYParty(role, address, port, LT, bitlen, nthreads, mt_alg);
    std::cout << "init sru success!" << std::endl;

}

void init_kd_aby(std::string address, uint16_t port, bool role_is_server) {
    e_role role;
    if (role_is_server) {
        role = (e_role) 0;
    } else {
        role = (e_role) 1;
    }

    kd_party = new ABYParty(role, address, port, LT, gbitlen, nthreads, mt_alg);
    std::cout << "init kd success!" << std::endl;
}

void shutdown_sru_aby() {
    delete sru_party;
    std::cout << "shutdown sru successs!" << std::endl;
}
void shutdown_kd_aby() {
    delete kd_party;
    std::cout << "shutdown kd successs!" << std::endl;
}

void reset_sru_aby() {
    sru_party->Reset();
}

void reset_kd_aby() {
    kd_party->Reset();
}

std::vector<uint8_t> kd_sru(bool role, std::vector<uint8_t> *idx, uint32_t num_workers, uint32_t length, int f) {
    std::vector<Sharing *> &sharings = sru_party->GetSharings();
    ArithmeticCircuit *ac = (ArithmeticCircuit *) sharings[S_ARITH]->GetCircuitBuildRoutine();
    BooleanCircuit *yc = (BooleanCircuit *) sharings[S_YAO]->GetCircuitBuildRoutine();
    BooleanCircuit *bc = (BooleanCircuit *) sharings[S_BOOL]->GetCircuitBuildRoutine();

    share **s_vec1 = (share **) malloc(sizeof(share *) * num_workers);
    share **s_vec2 = (share **) malloc(sizeof(share *) * num_workers);

    if (role) {
        for (int i = 0; i < num_workers; ++i) {
            s_vec1[i] = bc->PutSIMDINGate(length, idx->data() + i * length, bitlen, SERVER);
            s_vec2[i] = bc->PutDummySIMDINGate(length, bitlen);
        }
    } else {
        for (int i = 0; i < num_workers; ++i) {
            s_vec2[i] = bc->PutSIMDINGate(length, idx->data() + i * length, bitlen, CLIENT);
            s_vec1[i] = bc->PutDummySIMDINGate(length, bitlen);
        }
    }

    share **s_xor = (share **) malloc(sizeof(share *) * num_workers);
    for (int i = 0; i < num_workers; ++i) {
        s_xor[i] = bc->PutXORGate(s_vec1[i], s_vec2[i]);
    }

    share *s_sru = BuildSRUCircuit(s_xor, num_workers, f, length, ac, bc, yc);

    share *s_out = bc->PutSharedOUTGate(s_sru);
    sru_party->ExecCircuit();

    uint32_t *output;
    uint32_t out_bitlen, out_nvals;
    s_out->get_clear_value_vec(&output, &out_bitlen, &out_nvals);

    std::vector<uint8_t> v_out;

    for (int i = 0; i < length; i++) {
        v_out.push_back(output[i] % 2);
    }

    for (int i = 0; i < num_workers; ++i) {
        delete s_vec1[i];
        delete s_vec2[i];
        delete s_xor[i];
    }

    delete s_vec1;
    delete s_vec2;
    delete s_xor;

    reset_sru_aby() ;
    return v_out;
}

share *
BuildSRUCircuit(share **s_xor, uint32_t num_workers, uint32_t f, uint32_t length, ArithmeticCircuit *ac,
                BooleanCircuit *bc,
                BooleanCircuit *yc) {

    uint8_t _one = 1, _zero = 0;
    share *s_one = yc->PutSIMDCONSGate(length, _one, bitlen);
    share *s_zero = yc->PutSIMDCONSGate(length, _zero, bitlen);
    share *s_f = yc->PutSIMDCONSGate(length, f, bitlen);

    s_xor[0] = ac->PutB2AGate(s_xor[0]);
    for (int i = 1; i < num_workers; ++i) {
        s_xor[i] = ac->PutB2AGate(s_xor[i]);
        s_xor[0] = ac->PutADDGate(s_xor[0], s_xor[i]);
    }

    s_xor[0] = yc->PutA2YGate(s_xor[0]);

    share *gt = yc->PutGTGate(s_xor[0], s_f);
    s_xor[0] = yc->PutMUXGate(s_one, s_zero, gt);
    s_xor[0] = bc->PutY2BGate(s_xor[0]);

    return s_xor[0];
}


std::vector<uint32_t>
kd_top(bool role, std::vector<uint32_t> *grad, std::vector<uint32_t> *fgrad, uint32_t k, uint32_t num_workers, uint32_t f) {

    std::vector<Sharing *> &sharings = kd_party->GetSharings();

    BooleanCircuit *bc = (BooleanCircuit *) sharings[S_BOOL]->GetCircuitBuildRoutine();
    BooleanCircuit *yc = (BooleanCircuit *) sharings[S_YAO]->GetCircuitBuildRoutine();
    ArithmeticCircuit *ac = (ArithmeticCircuit *) sharings[S_ARITH]->GetCircuitBuildRoutine();

    share **st_vec1 = (share **) malloc(sizeof(share *) * num_workers);
    share **st_vec2 = (share **) malloc(sizeof(share *) * num_workers);
    share **st_fvec1 = (share **) malloc(sizeof(share *) * num_workers);
    share **st_fvec2 = (share **) malloc(sizeof(share *) * num_workers);

    if (role) {
        for (int i = 0; i < num_workers; i++) {
            st_vec1[i] = ac->PutSIMDINGate(k, grad->data() + i * k, gbitlen, SERVER);
            st_fvec1[i] = ac->PutSIMDINGate(k, fgrad->data() + i * k, gbitlen, SERVER);
            st_vec2[i] = ac->PutDummySIMDINGate(k, gbitlen);
            st_fvec2[i] = ac->PutDummySIMDINGate(k, gbitlen);
        }

    } else {
        for (int i = 0; i < num_workers; i++) {
            st_vec2[i] = ac->PutSIMDINGate(k, grad->data() + i * k, gbitlen, CLIENT);
            st_fvec2[i] = ac->PutSIMDINGate(k, fgrad->data() + i * k, gbitlen, CLIENT);
            st_vec1[i] = ac->PutDummySIMDINGate(k, gbitlen);
            st_fvec1[i] = ac->PutDummySIMDINGate(k, gbitlen);
        }

    }

    for (int i = 0; i < num_workers; ++i) {
        st_vec1[i] = ac->PutADDGate(st_vec1[i], st_vec2[i]);
        st_fvec1[i] = ac->PutADDGate(st_fvec1[i], st_fvec2[i]);
    }

    share *st_grad, *st_out;

    st_grad = BuildTOPCircuit(st_vec1, st_fvec1, num_workers, f, ac, bc, yc);
    st_out = ac->PutOUTGate(st_grad, ALL);

    kd_party->ExecCircuit();

    uint32_t *output;
    uint32_t out_bitlen, out_nvals;
    st_out->get_clear_value_vec(&output, &out_bitlen, &out_nvals);

    std::vector<uint32_t> v_out;
    for (int i = 0; i < k; i++) {
        v_out.push_back(output[i]);
    }

    for (int i = 0; i < num_workers; ++i) {
        delete st_vec1[i];
        delete st_vec2[i];
        delete st_fvec1[i];
        delete st_fvec2[i];
    }

    delete st_vec1;
    delete st_vec2;
    delete st_fvec1;
    delete st_fvec2;

    reset_kd_aby();
    return v_out;
}

share *BuildTOPCircuit(share **s_grad, share **s_fgrad, uint32_t num_workers, uint32_t f, ArithmeticCircuit *ac, BooleanCircuit *bc,
                       BooleanCircuit *yc) {

    share **st_ygrad = (share **) malloc(sizeof(share *) * num_workers);
    share **st_yfgrad = (share **) malloc(sizeof(share *) * num_workers);

    share *s_omax, *s_omin;
    share *s_fmax, *s_fmin;
    share *s_max, *s_min;

    for (int i = 0; i < num_workers; ++i) {
        st_ygrad[i] = yc->PutA2YGate(s_grad[i]);
        st_yfgrad[i] = yc->PutA2YGate(s_fgrad[i]);
    }
    s_omax = yc->PutMaxGate(st_ygrad, num_workers);
    s_fmax = yc->PutMaxGate(st_yfgrad, num_workers);
    s_omin = yc->PutMinGate(st_ygrad, num_workers);
    s_fmin = yc->PutMinGate(st_yfgrad, num_workers);

    share *s_amax = bc->PutY2BGate(s_omax);
    s_amax = ac->PutB2AGate(s_amax);
    share *s_amin = bc->PutY2BGate(s_omin);
    s_amin = ac->PutB2AGate(s_amin);

    share *s_afmax = bc->PutY2BGate(s_fmax);
    s_afmax = ac->PutB2AGate(s_afmax);
    share *s_afmin = bc->PutY2BGate(s_fmin);
    s_afmin = ac->PutB2AGate(s_afmin);

    share *distance = ac->PutSUBGate(s_afmax, s_afmin);

    s_max = ac->PutSUBGate(s_amax, distance);
    s_min = ac->PutADDGate(s_amin, distance);

    share *s_ymax = yc->PutA2YGate(s_max);
    share *s_ymin = yc->PutA2YGate(s_min);

    share **s_gt = (share **) malloc(sizeof(share *) * num_workers);

    share **s_score = (share **) malloc(sizeof(share *) * num_workers);

    for (int i = 0; i < num_workers; ++i) {
        s_gt[i] = yc->PutGTGate(st_ygrad[i], s_ymax);
        s_gt[i] = yc->PutORGate(s_gt[i], yc->PutGTGate(s_ymin, st_ygrad[i]));

        s_gt[i] = bc->PutY2BGate(s_gt[i]);
        s_gt[i] = ac->PutB2AGate(s_gt[i]);

        s_gt[i] = ac->PutSplitterGate(s_gt[i]);

        for (int j = 1; j < s_grad[0]->get_nvals(); ++j) {
            s_gt[i]->set_wire_id(0, ac->PutADDGate(s_gt[i]->get_wire_id(0), s_gt[i]->get_wire_id(j)));
        }
        s_score[i] = s_gt[i]->get_wire_ids_as_share(0);
        s_score[i] = yc->PutA2YGate(s_score[i]);
    }
    int nvals = s_grad[0]->get_nvals();

    for (int i = 0; i < f; ++i) {
        for (int j = i + 1; j < num_workers; ++j) {
            share *s_tmp_gt = yc->PutGTGate(s_score[i], s_score[j]);
            share *s_tmp = s_score[i];
            s_score[i] = yc->PutMUXGate(s_score[j], s_score[i], s_tmp_gt);
            s_score[j] = yc->PutMUXGate(s_tmp, s_score[j], s_tmp_gt);

            s_tmp_gt = yc->PutRepeaterGate(nvals, s_tmp_gt);
            s_tmp = st_ygrad[i];
            st_ygrad[i] = yc->PutMUXGate(st_ygrad[j], st_ygrad[i], s_tmp_gt);
            st_ygrad[j] = yc->PutMUXGate(s_tmp, st_ygrad[j], s_tmp_gt);

            s_grad[i] = bc->PutY2BGate(st_ygrad[i]);
            s_grad[i] = ac->PutB2AGate(s_grad[i]);
        }
    }


    for (int i = 1; i < f; ++i) {
        s_grad[0] = ac->PutADDGate(s_grad[0], s_grad[i]);
    }

    for (int i = 0; i < num_workers; ++i) {
        delete st_ygrad[i];
        delete st_yfgrad[i];
        delete s_score[i];
        delete s_gt[i];
    }
    delete st_ygrad;
    delete st_yfgrad;
    delete s_score;
    delete s_gt;

    return s_grad[0];

}

