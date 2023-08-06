use num::Integer;

pub fn bit_flip(state: usize, index: usize) -> usize {
    state ^ (1 << index)
}

pub fn bit_flip_vec(mut state: Vec<u64>, index: usize) -> Vec<u64> {
    let (outer_index, inner_index) = index.div_mod_floor(&64);
    state[outer_index] = bit_flip(state[outer_index] as usize, inner_index) as u64;
    state
}

pub fn is_one_at(state: usize, target: usize) -> bool {
    state & (1 << target) != 0
}

pub fn is_one_at_vec(state: &[u64], target: usize) -> bool {
    let (outer_index, inner_index) = target.div_mod_floor(&64);
    state[outer_index] & (1 << inner_index) != 0
}

pub fn ctrl_check(state: usize, control: &[usize]) -> bool {
    control.iter().all(|control| is_one_at(state, *control))
}

pub fn ctrl_check_vec(state: &[u64], control: &[usize]) -> bool {
    control.iter().all(|control| is_one_at_vec(state, *control))
}

pub fn pown(mut x: u64, mut a: u64, n: u64) -> u64 {
    if a == 0 {
        return 1;
    }

    let mut y = 1;
    while a > 1 {
        if (a & 1) != 0 {
            y = (y * x) % n
        };
        x = (x * x) % n;

        a >>= 1;
    }

    (x * y) % n
}

pub fn bit_len(mut num: u64) -> u64 {
    let mut len = 0;
    while num != 0 {
        num >>= 1;
        len += 1;
    }
    len
}
