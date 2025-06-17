import math

class Action:
    
    @staticmethod
    def shoot(robot, ball, power: float = 5.0):
        """Robot thực hiện sút bóng nếu có bóng và bóng ở gần phía trước."""
        if not getattr(robot, 'has_ball', False):
            print("[Shoot] ❌ Robot không có bóng để sút.")
            return False

        rx, ry = robot.pose['x'], robot.pose['y']
        theta_deg = robot.pose['theta']
        theta_rad = math.radians(theta_deg)

        bx, by = ball.get_position()
        dx, dy = bx - rx, by - ry
        dist = math.hypot(dx, dy)

        robot_radius = 0.25
        ball_radius = ball.radius
        max_shoot_dist = robot_radius + ball_radius + 0.05

        if dist > max_shoot_dist:
            print("[Shoot] ❌ Quá xa để sút.")
            return False

        
        front_dx =  math.cos(theta_rad)
        front_dy =  math.sin(theta_rad)
        dot = front_dx * dx + front_dy * dy

        if dot < 0:
            print("[Shoot] ❌ Bóng không ở phía trước.")
            return False

        ball.kick(power, theta_rad, robot.team)
        robot.has_ball = False
        print(f"[Shoot] ✅ Robot {robot.robot_id} (Team {robot.team}) đã sút bóng với lực {power:.1f}N.")
        return True
   
   
    
    '''
    def pass_ball(robot, teammates, ball, power: float = 4.0):
        """Robot chuyền bóng cho đồng đội gần nhất ở phía trước nếu có bóng."""
        if not getattr(robot, 'has_ball', False):
            print("[Pass] ❌ Robot không có bóng để chuyền.")
            return False

        if not teammates:
            print("[Pass] ❌ Không có đồng đội nào.")
            return False

        rx, ry = robot.pose['x'], robot.pose['y']
        theta_deg = robot.pose['theta']
        theta_rad = math.radians(theta_deg)

        front_dx = math.cos(theta_rad)
        front_dy = math.sin(theta_rad)

        min_dist = float("inf")
        target = None

        for mate in teammates:
            mx, my = mate.pose['x'], mate.pose['y']
            dx, dy = mx - rx, my - ry
            dot = front_dx * dx + front_dy * dy
            if dot > 0.2:  # phía trước
                dist = math.hypot(dx, dy)
                if dist < min_dist:
                    min_dist = dist
                    target = mate

        if target is None:
            print("[Pass] ❌ Không tìm thấy đồng đội phía trước.")
            return False

        tx, ty = target.pose['x'], target.pose['y']
        angle = math.atan2(ty - ry, tx - rx)

        ball.kick(power, angle, robot.team)
        robot.has_ball = False
        print(f"[Pass] ✅ Robot {robot.robot_id} chuyền bóng cho {target.robot_id}.")
        return True
    '''
    @staticmethod
    def pass_ball(robot, teammates, ball, power=4.0):
        if not getattr(robot, 'has_ball', False):
            print("[Pass] ❌ Robot không có bóng để chuyền.")
            return False

        if not teammates:
            print("[Pass] ❌ Không có đồng đội nào để chuyền.")
            return False

        rx, ry = robot.pose['x'], robot.pose['y']
        theta_rad = math.radians(robot.pose['theta'])
         
        front_dx =  math.cos(theta_rad)
        front_dy =  math.sin(theta_rad)

        # Tìm teammate gần nhất phía trước
        min_dist = float("inf")
        target = None
        for mate in teammates:
            mx, my = mate.pose['x'], mate.pose['y']
            dx = mx - rx
            dy = my - ry
            dot = front_dx * dx + front_dy * dy
            if dot > 0.1:  # teammate phía trước
                dist = math.hypot(dx, dy)
                if dist < min_dist:
                    min_dist = dist
                    target = mate

        if target is None:
            print("[Pass] ❌ Không tìm thấy đồng đội phía trước.")
            return False

        # Tính góc sút hướng về teammate
        tx, ty = target.pose['x'], target.pose['y']
        dx = tx - rx
        dy = ty - ry
        angle_rad = math.atan2(dy, dx)
        '''
        if robot.team == 1:
            angle_rad = math.atan2(dy, dx)
        else: 
            angle_rad = math.atan2(dy, dx)+ math.pi
        '''
        # Thực hiện chuyền bóng
        ball.kick(power, angle_rad, robot.team)
        robot.has_ball = False
        print(f"[Pass] ✅ Robot {robot.robot_id} Team {robot.team} chuyền cho Robot {target.robot_id}")
        return True



    @staticmethod
    def catch_ball(robot, ball):
        """Robot cố gắng bắt bóng nếu bóng ở gần và phía trước."""
        rx, ry = robot.pose['x'], robot.pose['y']
        bx, by = ball.get_position()
        theta_deg = robot.pose['theta']
        theta_rad = math.radians(theta_deg)

        dx, dy = bx - rx, by - ry
        dist = math.hypot(dx, dy)

        robot_radius = 0.25
        ball_radius = ball.radius
        max_catch_dist = robot_radius + ball_radius + 0.1

        if dist > max_catch_dist:
            print("[Catch] ❌ Quá xa để bắt bóng.")
            return False

        front_dx = math.cos(theta_rad)
        front_dy = math.sin(theta_rad)
        dot = front_dx * dx + front_dy * dy

        if dot < 0.2:
            print("[Catch] ❌ Bóng không ở phía trước.")
            return False

        hold_dist = robot_radius + ball_radius + 0.01
        new_bx = rx + hold_dist * front_dx
        new_by = ry + hold_dist * front_dy

        ball.set_position(new_bx, new_by)
        ball.vx = 0
        ball.vy = 0
        robot.has_ball = True
        print(f"[Catch] ✅ Robot {robot.robot_id} đã bắt bóng.")
        return True

    @staticmethod
    def keep_ball(robot, ball):
        rx, ry = robot.pose['x'], robot.pose['y']
        theta_rad = math.radians(robot.pose['theta'])

        bx, by = ball.get_position()
        dx = bx - rx
        dy = by - ry
        dist = math.hypot(dx, dy)

        robot_radius = 0.25
        ball_radius = ball.radius
        max_hold_dist = robot_radius + ball_radius + 0.01

        if dist <= max_hold_dist:
            # Sửa lại hướng theo team
             
            front_dx = math.cos(theta_rad)
            front_dy = math.sin(theta_rad)

            dot = front_dx * dx + front_dy * dy

            if dot > 0.3:
                hold_x = rx + (robot_radius + ball_radius + 0.01) * front_dx
                hold_y = ry + (robot_radius + ball_radius + 0.01) * front_dy
                ball.set_position(hold_x, hold_y)
                ball.vx = 0
                ball.vy = 0
                robot.has_ball = True
                return True

        robot.has_ball = False
        return False

