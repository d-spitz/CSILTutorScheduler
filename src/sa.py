from simanneal import Annealer
import random
import scorer
import const_csil_params
import schedule

# This is the class that actually does the annealing. It defines 3 important methods:
# an initializer (creates random tutor schedule assigment),
# a mover (swaps two random tutor assignemnts),
# and an energy scorer (evaluates the schedule quantitatively)
# 
# These are used in the Annealer class to run simulated annealing and find an
# approximate optimal solution to this scheduling problem


class ScheduleAnnealer(Annealer):
    # Stores the data of all csil tutors
    csil_tutors_info = None
    
    # Schedule wrapper for printing
    schedule = None

    # State the stores weekly tutor schedule for annealing
    state = None

    # Initializes the annealing process given a filename pointing to a csv with
    # the form output, and sets a random tutor assignment to the starting state
    def __init__(self, csil_tutors_info):
        self.csil_tutors_info = csil_tutors_info
        self.schedule = schedule.Schedule(csil_tutors_info)
        self.state = self.schedule.state
        self.initialize_state()
        # necessary for Annealer
        super(ScheduleAnnealer, self).__init__(self.state)

    # Matches schedule.state and self.state for printing
    def update_schedule_state_post_anneal(self, state):
        self.schedule.state = state

    # Gets a list of random correct (non_conflicting) blocks in the weekly schedule as a (day, block) 
    # index pair, non-repeating
    def get_random_correct_blocks(self, tid, num):
        smp_space = self.csil_tutors_info.tutors_info[tid].available_indices
        return random.sample(smp_space, num)
    
    # Gets one random block from the schedule
    def get_random_block(self):
        d = random.randrange(0, len(self.state))
        return (d, random.randrange(0, const_csil_params.BLOCKS_PER_DAY[d]))
    
    # Checks if a given move would be correct, if tid is not none, then it represents
    # A move from that tid in i1 to i2, or i2 to i1, for tid1,2 respectively
    def is_move_correct(self, i1, i2, tid1=None, tid2=None):
        ans = False
        if tid1 == None:
            # Move from i2 to i1
            ans = i1 not in self.csil_tutors_info.tutors_info[tid2].conflicts_indices
        elif tid2 == None:
            ans = i2 not in self.csil_tutors_info.tutors_info[tid1].conflicts_indices
        return ans

    # Initializes the state with random tutor block assignments, each one is given
    # their preferred number of shift hours
    # Initialize with correctness: no tutor is assigned to conflicting block
    def initialize_state(self):
        for tid in range(self.csil_tutors_info.num_tutors):
            tutor = self.csil_tutors_info.tutors_info[tid]
            avail_blocks = tutor.available_indices
            if len(avail_blocks) < tutor.total_blocks:
                print(tutor.total_blocks, "Tutor " + tutor.name + " has fewer available blocks than requested, so their hours will be reduced.")
                tutor.total_blocks = len(avail_blocks)
            pref_num_shifts = tutor.total_blocks
            blks = self.get_random_correct_blocks(tid, pref_num_shifts)
            for d, b in blks:
                self.state[d][b].add(tid)
        return 

    # Randomly swaps two tutor assignments in the state
    # Only makes meaningful changes (never moving tutor to block they are
    # already assigned to)
    # Only makes correct changes (no moving tutor to conflicting block)
    def move(self):
        d1, b1 = self.get_random_block()
        d2, b2 = self.get_random_block()
        s1 = self.state[d1][b1]
        s2 = self.state[d2][b2]
        s1_diff = s1.difference(s2)
        s2_diff = s2.difference(s1)
        if len(s1_diff) == 0 and len(s2_diff) == 0:
            return 0
        elif len(s1_diff) == 0:
            rnd_tid = random.choice(tuple(s2_diff))
            if self.is_move_correct((d1, b1), (d2, b2), None, rnd_tid):
                s2.remove(rnd_tid)
                s1.add(rnd_tid)
                return None
            return 0
        elif len(s2_diff) == 0:
            rnd_tid = random.choice(tuple(s1_diff))
            if self.is_move_correct((d1, b1), (d2, b2), rnd_tid, None):
                s1.remove(rnd_tid)
                s2.add(rnd_tid)
                return None
            return 0
        else:
            rnd_tid1 = random.choice(tuple(s1_diff))
            rnd_tid2 = random.choice(tuple(s2_diff))
            any_success = False
            if self.is_move_correct((d1, b1), (d2, b2), rnd_tid1, None):
                s1.remove(rnd_tid1)
                s2.add(rnd_tid1)
                any_success = True
            if self.is_move_correct((d1, b1), (d2, b2), None, rnd_tid2):
                s2.remove(rnd_tid2)
                s1.add(rnd_tid2)
                any_success = True
            return None if any_success else 0
        return None

    # calculats the total evaluation score of the state
    # we want to minimize the energy, so we negate the score
    # scoring is separated into the Scorer class
    def energy(self):
        return -scorer.Scorer.get_schedule_score(self.state, self.csil_tutors_info)    
