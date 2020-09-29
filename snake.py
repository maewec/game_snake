# -*- coding: utf-8 -*-
"""
Snake is multiplayer game with bots.
"""

import tkinter as tk
from random import randint, choice


class Pole:
    def __init__(self, master, width, height, scale, bg='white'):
        self.master = master
        self.width = width
        self.height = height
        self.width_real = width * scale
        self.height_real = height * scale
        self.scale = scale
        self.bg = bg

        self.pole = tk.Canvas(self.master, width=self.width_real,
                              height=self.height_real, bg=self.bg)
        self.pole.pack()

        self.snakes = []
        self.eats = []

    def get_scale(self):
        return self.scale

    def set_snakes(self, num):
        for i in range(num):
            self.snakes.append(Snake(self))

    def set_eats(self, num):
        for i in range(num):
            self.eats.append(Eat(self))

class Information:
    def __init__(self, master):
        self.master = master
        self.label = tk.Label(master)
        self.label.pack()

    def update(self, snake):
        x, y = snake.body[0].get_coords()
        length = snake.length
        speed = snake.speed
        string = 'X = {}, Y = {}, length = {}, speed = {}'.format(x, y, length, speed)
        self.label['text'] = string


class Elem:
    def __init__(self, pole, x, y, color='black'):
        self.pole = pole
        self.x = x
        self.y = y
        self.color = color
        self.scale = self.pole.get_scale()
        x0, y0, x1, y1 = self.real_coords()

        self.elem = self.pole.pole.create_rectangle(x0, y0, x1, y1, fill=color)

    def real_coords(self):
        x0 = self.x * self.scale + 1
        y0 = self.y * self.scale + 1
        x1 = (self.x + 1) * self.scale
        y1 = (self.y + 1) * self.scale
        return x0, y0, x1, y1

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.x = self.x % self.pole.width
        self.y = self.y % self.pole.height
        x0, y0, x1, y1 = self.real_coords()
        self.pole.pole.coords(self.elem, x0, y0, x1, y1)

    def check_move(self, dx, dy):
        return self.x + dx, self.y +dy

    def teleport(self, x, y):
        self.x = x
        self.y = y
        self.x = self.x % self.pole.width
        self.y = self.y % self.pole.height
        x0, y0, x1, y1 = self.real_coords()
        self.pole.pole.coords(self.elem, x0, y0, x1, y1)

    def get_coords(self):
        return self.x, self.y

    def destroy(self):
        self.pole.pole.delete(self.elem)

    def set_color(self, color):
        self.color = color
        self.pole.pole.itemconfig(self.elem, fill=color)


color_snake = ('black', 'blue', 'cyan', 'gray', 'cyan', 'orange') * 5

class Snake:
    count = 0
    def __init__(self, pole):
        self.id = Snake.count                                                   # идентификатор объекта
        Snake.count +=1

        self.pole = pole
        self.direction = 'r'
        self.speed = 10                                                         # клеток в секунду
        self.job = None
        self.length = 1
        width = pole.width
        height = pole.height
        x = randint(0, width-1)
        y = randint(0, height-1)
        self.body = [Elem(self.pole, x, y, color=color_snake[self.id])]

        self.info = Information(self.pole.master)

        self.previos_move = [0, 0]

    def growth(self, eat):
        x, y = eat.get_coords()
        color = eat.color
        self.body.insert(1, Elem(self.pole, x, y, color))

    def move(self):                                                               # сюда засовываем еду, чтобы при поедании новый объект появлялся

        gameover = False                                                        # если флаг меняется, то игра останавливается

        dx, dy = 0, 0
        if self.direction == 'r': dx = 1
        if self.direction == 'l': dx = -1
        if self.direction == 'd': dy = 1
        if self.direction == 'u': dy = -1

        if self.previos_move == [dx * -1, dy * -1]:
            dx = self.previos_move[0]
            dy = self.previos_move[1]

        eat = True                                                              # если съел, то ключ меняется на false и движение в этом такте не происходит
        for i in range(len(self.pole.eats)):
            if self.get_coords() == self.pole.eats[i].get_coords():               # съел, удалил старый, добавил новый
                self.length += 1
                self.growth(self.pole.eats[i])
                self.pole.eats[i].destroy()
                self.pole.eats[i] = Eat(self.pole)
                eat = False
                break
        if eat:
            for i in range(len(self.body)-1, 0, -1):                                # от последнего элемента до второго
                x, y = self.body[i-1].get_coords()
                self.body[i].teleport(x, y)
            self.body[0].move(dx, dy)                                               # голову отдельно перемещаем

            # обработка препятствия в виде своего хвоста
            for i in self.get_list_coords_tail():                                   # если голова попала на препятствие, то проигрыш
                if self.get_coords() == i:
                    print('game over')
                    self.pole.master.after_cancel(self.job)
                    gameover = True
                    self.set_color('red')
                    break
            for sn in self.pole.snakes:
                if self.id != sn.id:                                            # отсекаем тот же объект змеи в списке
                    for i in sn.get_list_coords():
                        if self.get_coords() == i:
                            print('game over')
                            self.pole.master.after_cancel(self.job)
                            gameover = True
                            self.set_color('red')
                            break

        self.info.update(self)                                                       # обновление счета
        if gameover == False:
            self.job = self.pole.master.after(self.get_time_speed(), self.move)                # записываем в переменую, чтобы потом уничтожить
        self.previos_move = [dx, dy]

    def direct(self, direction):
        self.direction = direction
        if self.job:
            self.pole.master.after_cancel(self.job)                             # штука уничтожает процесс after
        self.move()

    def get_coords(self):
        return self.body[0].get_coords()

    def get_list_coords_tail(self):
        return (i.get_coords() for i in self.body[1:])

    def get_list_coords(self):
        return (i.get_coords() for i in self.body)

    def get_time_speed(self):
        return int(1000 / self.speed)

    def set_color(self, color):
        for el in self.body:
            el.set_color(color)

class Snake_bot(Snake):
    def search(self):
        xe, ye = self.pole.eats[0].get_coords()
        xs, ys = self.get_coords()
        for eat in self.pole.eats[1:]:
            xe_, ye_ = eat.get_coords()
            if abs(xe_ - xs + ye_ - ys) < abs(xe - xs + ye - xs):
                xe = xe_
                ye = ye_
        dx = xe - xs
        dy = ye - ys
        rand = randint(0,1)
        if dx == 0 and dy == 0:
            pass
        elif dx == 0:
            if dy > 0:
                self.direct('d')
            else:
                self.direct('u')
        elif dy == 0:
            if dx > 0:
                self.direct('r')
            else:
                self.direct('l')
        else:
            if rand == 0:
                if dx > 0:
                    self.direct('r')
                else:
                    self.direct('l')
            else:
                if dy > 0:
                    self.direct('d')
                else:
                    self.direct('u')
        self.pole.master.after(self.get_time_speed(), self.search)


lst_color_eat = ('green', 'blue', 'yellow', 'pink', 'gray', 'cyan', 'orange')
lst_color_eat =('yellow',)

class Eat:
    def __init__(self, pole):
        self.pole = pole
        self.color = choice(lst_color_eat)
        width = pole.width
        height = pole.height
        x = randint(0, width-1)
        y = randint(0, height-1)
        self.eat = Elem(self.pole, x, y, color=self.color)

    def destroy(self):
        self.eat.destroy()

    def get_coords(self):
        return self.eat.get_coords()






def main():

    root = tk.Tk()
    root.title('Змеюка')
    pole = Pole(root, width=80, height=45, scale=20)
    info = Information(root)
    #pole.set_snakes(3)
    pole.set_eats(20)

    Snake_bot(pole).search()
    Snake_bot(pole).search()
    Snake_bot(pole).search()
    Snake_bot(pole).search()
    Snake_bot(pole).search()
    Snake_bot(pole).search()
    Snake_bot(pole).search()
    Snake_bot(pole).search()
    Snake_bot(pole).search()
    Snake_bot(pole).search()



    #root.bind('<Left>', lambda event: pole.snakes[0].direct('l'))
    #root.bind('<Right>', lambda event: pole.snakes[0].direct('r'))
    #root.bind('<Up>', lambda event: pole.snakes[0].direct('u'))
    #root.bind('<Down>', lambda event: pole.snakes[0].direct('d'))
    #
    #root.bind('a', lambda event: pole.snakes[1].direct('l'))
    #root.bind('d', lambda event: pole.snakes[1].direct('r'))
    #root.bind('w', lambda event: pole.snakes[1].direct('u'))
    #root.bind('s', lambda event: pole.snakes[1].direct('d'))
    #
    #root.bind('h', lambda event: pole.snakes[2].direct('l'))
    #root.bind('k', lambda event: pole.snakes[2].direct('r'))
    #root.bind('u', lambda event: pole.snakes[2].direct('u'))
    #root.bind('j', lambda event: pole.snakes[2].direct('d'))

    root.mainloop()

if __name__ == '__main__':
    main()
