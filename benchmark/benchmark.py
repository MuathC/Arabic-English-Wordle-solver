import time
from tqdm import tqdm

from agents.frequency_agent import FrequencyAgent
from env.wordle_env import WordleEnv
from agents.CSP_agent import CSP_agent
from agents.entropy_agent import EntropyAgent
from agents.bayesian_agent import BayesianAgent


def benchmark(agents, n_games=100,language = "en", debug=False):
    results = {}

    for agent_class in agents:
        print(f"\nBenchmarking {agent_class.__name__}...\n")
        total_guesses = 0
        total_time = 0
        wins = 0

        for _ in tqdm(range(n_games), desc=f"{agent_class.__name__} Games"):

            env = WordleEnv(language = language)
            secret = env.reset()
            agent = agent_class(language = language)
            agent.reset()

            start = time.time()
            while not env.game_over:

                guess = agent.get_guess()
                feedback = env.guess(guess)
                agent.update(guess, feedback)

            if env.guesses[-1] == secret:
                wins += 1
                total_guesses += env.guess_count

            if debug:
                env.render()

                

            end = time.time()
            total_time += (end - start)

        avg_guesses = total_guesses / wins if wins > 0 else float('inf')
        win_rate = (wins / n_games) * 100
        avg_time = total_time / n_games

        results[agent_class.__name__] = (avg_guesses, win_rate, avg_time)
        print(f"\n{agent_class.__name__}: Avg guesses per win: {avg_guesses:.2f}, Win rate: {win_rate:.1f}%, Avg time: {avg_time:.2f}s\n")

    return results


def main(n_games = None,agents = None,language = "en" ):
    agents = agents or [CSP_agent]
    benchmark(agents, n_games=n_games or 100,language=language, debug=True)


def avg(n_trials=1, n_games=100,agents = None,language = "en"):
    agents = agents or [CSP_agent]
    MAX_GUESSES = 6

    stats = {
        agent.__name__: {
            'guesses': 0.0,
            'win_rate': 0.0,
            'time': 0.0
        } for agent in agents
    }

    print(f"\nRunning {n_trials} benchmark trials per agent (each with {n_games} games)...\n")

    with tqdm(total=n_trials, desc="Overall Trials",position=0) as trial_bar:
        for trial in range(n_trials):
            for agent_class in agents:
                agent_name = agent_class.__name__
                # Nested bar for the games of the current trial
            
                game_bar = tqdm(total=n_games, desc=f"{agent_name} Trial {trial + 1}", position = 2,leave=False)

                total_guesses = 0
                total_time = 0
                wins = 0

                for _ in range(n_games):
                    
                    env = WordleEnv(language = language)
                    secret = env.reset()
                    agent = agent_class(language = language)
                    agent.reset()
                    start = time.time()
                    while not env.game_over:
                        guess = agent.get_guess()
                        feedback = env.guess(guess)
                        agent.update(guess, feedback)

                    if env.guesses[-1] == secret:
                        wins += 1
                        total_guesses += env.guess_count

                    end = time.time()
                    total_time += (end - start)
                    game_bar.update(1)

                game_bar.close()

                avg_guesses = total_guesses / wins if wins > 0 else float('inf')
                win_rate = (wins / n_games) * 100
                avg_time = total_time / n_games

                safe_guesses = avg_guesses if avg_guesses != float('inf') else MAX_GUESSES
                stats[agent_name]['guesses'] += safe_guesses
                stats[agent_name]['win_rate'] += win_rate
                stats[agent_name]['time'] += avg_time

            trial_bar.update(1)

    print("\n=== Average of Averages ===")
    for agent_name, values in stats.items():
        avg_guesses = values['guesses'] / n_trials
        avg_winrate = values['win_rate'] / n_trials
        avg_time = values['time'] / n_trials
        print(f"{agent_name}: Avg of Avg Guesses = {avg_guesses:.2f}, Avg Win Rate = {avg_winrate:.2f}%, Avg Time = {avg_time:.2f}s")
    print()