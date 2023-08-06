from skyeye import remote



def command_env(env=None):
    if env is None:
        result = remote.get_current_env()
        print(f"current env:{result['env']} this cloud linked:{result['tip']}")
        return
    remote.switch_env(env)
