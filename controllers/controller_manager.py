import pygame

class ControllerManager:

    @staticmethod
    def setup_control(team, mode, strategy):
        controllers = []
        auto_robots = []

        if mode == 'Xbox':
            pygame.joystick.quit()
            pygame.joystick.init()
            num_joysticks = pygame.joystick.get_count()

            print(f"Found {num_joysticks} joysticks for team")

            for i, robot in enumerate(team.robots):
                if i < num_joysticks:
                    js = pygame.joystick.Joystick(i)
                    js.init()
                    controllers.append((robot, js))
                else:
                    auto_robots.append(robot)

        elif mode == 'Automation':
            auto_robots = team.robots[:]

        return controllers, auto_robots, strategy
