#include "canonical_pdbs.h"

#include "pattern_database.h"

#include <algorithm>
#include <cassert>
#include <iostream>
#include <limits>
#include "../utils/logging.h"

using namespace std;

namespace pdbs {


CanonicalPDBs::CanonicalPDBs(
    const shared_ptr<PDBCollection> &pdbs,
    const shared_ptr<vector<PatternClique>> &pattern_cliques)
    : pdbs(pdbs),
      pattern_cliques(pattern_cliques),
            heuristic_estimates_key("") {
    assert(pdbs);
    assert(pattern_cliques);
}

void CanonicalPDBs::set_heuristic_estimates_key(const std::string &key) {
    heuristic_estimates_key = key;
}

void CanonicalPDBs::print_values(const State& state) const {
    // If we have an empty collection, then pattern_cliques = { \emptyset }.
    assert(!pattern_cliques->empty());

    vector<int> h_values;
    h_values.reserve(pdbs->size());
    state.unpack();
    for (const shared_ptr<PatternDatabase> &pdb : *pdbs) {
        int h = pdb->get_value(state.get_unpacked_values());
        h_values.push_back(h);
    }

    std::cout << heuristic_estimates_key << ": " << h_values << std::endl;
}

int CanonicalPDBs::get_value(const State &state) const {
    // If we have an empty collection, then pattern_cliques = { \emptyset }.
    assert(!pattern_cliques->empty());
    int max_h = 0;
    vector<int> h_values;
    h_values.reserve(pdbs->size());
    state.unpack();
    for (const shared_ptr<PatternDatabase> &pdb : *pdbs) {
        int h = pdb->get_value(state.get_unpacked_values());
        if (h == numeric_limits<int>::max()) {
            return numeric_limits<int>::max();
        }
        h_values.push_back(h);
    }
    for (const PatternClique &clique : *pattern_cliques) {
        int clique_h = 0;
        for (PatternID pdb_index : clique) {
            clique_h += h_values[pdb_index];
        }
        max_h = max(max_h, clique_h);
    }

    print_values(state);

    return max_h;
}
}
