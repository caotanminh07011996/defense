import pygame

def assign_xbox_controllers(team):
    """
    Gán joystick Xbox cho các robot trong team. Nếu số joystick ít hơn số robot,
    phần còn lại sẽ điều khiển tự động (automation).
    
    Returns:
        controllers: list of (robot, joystick) tuples
        auto_robots: list of robots không có joystick
    """
    pygame.joystick.quit()
    pygame.joystick.init()

    num_joysticks = pygame.joystick.get_count()
    print(f"[Xbox Controller] Found {num_joysticks} joysticks for team {team.team_id}")

    controllers = []
    auto_robots = []

    for i, robot in enumerate(team.robots):
        if i < num_joysticks:
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            controllers.append((robot, joystick))
        else:
            auto_robots.append(robot)

    return controllers, auto_robots
