#ifndef PDBS_CANONICAL_PDBS_H
#define PDBS_CANONICAL_PDBS_H

#include "types.h"

#include <memory>
#include <string>

class State;

namespace pdbs {
class CanonicalPDBs {
    std::shared_ptr<PDBCollection> pdbs;
    std::shared_ptr<std::vector<PatternClique>> pattern_cliques;
    std::string heuristic_estimates_key;

public:
    CanonicalPDBs(
        const std::shared_ptr<PDBCollection> &pdbs,
        const std::shared_ptr<std::vector<PatternClique>> &pattern_cliques);
    ~CanonicalPDBs() = default;

    void set_heuristic_estimates_key(const std::string &key);

    void print_values(const State& state) const;

    int get_value(const State &state) const;
};
}

#endif
