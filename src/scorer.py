import const_csil_params
import weights

# Quantitatively assigns a weighted score to a given schedule state, based on the
# form parameters. Weights are defined in the weights file.
# Bigger score here = better, negated in annealer as energy is supposed to be minimized


class Scorer:
    # Given the state, a tutor id, and the tutors_info dict, scores
    # how close each tutor is to their preferred total number of hours working
    def score_total_blocks(state, tid, tutors_info):
        sum = 0
        for d in state:
            for b in d:
                if tid in b:
                    sum += 1
        return 1 - abs(sum - tutors_info[tid].total_blocks)

    # Given the state, a tutor id, and the tutors_info dict, scores
    # how close each tutor is to their preferred shift length
    # Also takes into account the number of shifts per day
    def score_shift_len(state, tid, tutors_info):
        target = 0
        target_shifts_per_day = 1
        longer = const_csil_params.SHIFT_LEN_CODES["Longer shifts (fewer days)"]
        shorter = const_csil_params.SHIFT_LEN_CODES["Shorter shifts (more days)"]
        nopref = const_csil_params.SHIFT_LEN_CODES["No preference!"]
        if tutors_info[tid].shift_len == longer:
            target = const_csil_params.LONG_SHIFT_LEN
        elif tutors_info[tid].shift_len == shorter:
            target = const_csil_params.SHORT_SHIFT_LEN
        elif tutors_info[tid].shift_len == nopref:
            return 0
        else:
            print("error: unrecognized shift length preference")
            return

        onstreak = False
        sumdiff = 0
        for d in state:
            if onstreak:
                sumdiff += abs(target - curshiftlen)
            shifts_per_day = 0
            onstreak = False
            curshiftlen = 0
            for b in d:
                if tid in b:
                    curshiftlen += 1
                    if not onstreak:
                        shifts_per_day += 1
                        onstreak = True
                else:
                    if onstreak:
                        sumdiff += abs(target - curshiftlen)
                        onstreak = False
                        curshiftlen = 0
            sumdiff += abs(target_shifts_per_day - shifts_per_day)
        if onstreak:
            sumdiff += abs(target - curshiftlen)

        return 10 - sumdiff

    # Given the state, a tutor id, and the tutors_info dict, scores
    # how many times the tutor is with their preferred desk mates
    def score_with_desk_mates(state, tid, tutors_info):
        sum = 0
        for d in state:
            for b in d:
                if tid in b:
                    for dm in tutors_info[tid].desk_mates:
                        if dm in b:
                            sum += 1
        return sum

    # Given the state, a tutor id, and the tutors_info dict, scores
    # how the state adheres to this tutors' scheduling conflicts/preferences
    def score_conflicts_preferences(state, tid, tutors_info):
        sum = 0
        noconf = const_csil_params.CONFLICT_TERMS_CODES["No conflict, not preferred"]
        pref = const_csil_params.CONFLICT_TERMS_CODES["Preferred shift"]
        conf = const_csil_params.CONFLICT_TERMS_CODES["Conflict"]
        for d in range(7):
            for b in range(const_csil_params.BLOCKS_PER_DAY[d]):
                if tid in state[d][b]:
                    conf_val = tutors_info[tid].conflicts_preferences.state[d][b]
                    if conf_val == noconf:
                        pass
                    elif conf_val == pref:
                        sum += 2
                    elif conf_val == conf:
                        sum -= 10
                    else:
                        print("Error: cannot understand this conflict code")
        return sum

    # Given the state, a tutor id, the tutors_info dict, and the teams_members dict,
    # scores how many times the tutor is with their teammembers
    def score_with_teammates(state, tid, tutors_info, teams_members):
        sum = 0
        for d in state:
            for b in d:
                if tid in b:
                    for tm in tutors_info[tid].teams:
                        for dm in tutors_info[tid].desk_mates:
                            if dm in teams_members[tm]:
                                sum += 1
        return sum

    # Given the state, scores how well the state adheres to the
    # min/max number of tutors on shift policy
    def overall_score_min_max_tutors_per_block(state):
        penalty = 0
        for d in state:
            for b in d:
                if len(b) < const_csil_params.MIN_TUTORS_ON_SHIFT:
                    penalty += abs(const_csil_params.MIN_TUTORS_ON_SHIFT - len(b))
                if len(b) > const_csil_params.MAX_TUTORS_ON_SHIFT:
                    penalty += abs(const_csil_params.MAX_TUTORS_ON_SHIFT - len(b))
        return 20 - penalty

    # Given the state and CSILTutorsInfo data, returns the overall weighted score
    # evaluating the current schedule
    def get_schedule_score(state, csil_tutors_info):
        score = 0
        num_tutors = csil_tutors_info.num_tutors
        tutors_info = csil_tutors_info.tutors_info
        teams_members = csil_tutors_info.teams_members
        total_blocks_w = weights.SCORING_WEIGHTS["total_blocks"]
        shift_len_w = weights.SCORING_WEIGHTS["shift_len"]
        desk_mates_w = weights.SCORING_WEIGHTS["desk_mates"]
        conflicts_preferences_w = weights.SCORING_WEIGHTS["conflicts_preferences"]
        teammates_w = weights.SCORING_WEIGHTS["teammates"]


        # Individual tutor scores
        for tid in range(num_tutors):
            temp_score = 0
            temp_score += Scorer.score_total_blocks(state, tid, tutors_info) * total_blocks_w
            temp_score += Scorer.score_shift_len(state, tid, tutors_info) * shift_len_w
            temp_score += Scorer.score_with_desk_mates(state, tid, tutors_info) * desk_mates_w
            temp_score += Scorer.score_conflicts_preferences(state, tid, tutors_info) * conflicts_preferences_w
            temp_score += Scorer.score_with_teammates(state, tid, tutors_info, teams_members) * teammates_w

            # Each tutor score is weighted by their seniority, weight can be adjusted in weights file
            score += temp_score * weights.SCORING_WEIGHTS["seniority"][tutors_info[tid].years_worked]

        # global constraint scores
        score += Scorer.overall_score_min_max_tutors_per_block(state) * weights.SCORING_WEIGHTS["min_max_tutors_per_block"]

        return score
