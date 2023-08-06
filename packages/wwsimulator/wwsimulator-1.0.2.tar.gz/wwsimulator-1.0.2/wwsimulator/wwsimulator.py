import random
import turtle
import tkinter as tk
from random import randint
from tkinter import messagebox
from tkinter import ttk



turtle.speed(0)
turtle.penup()

all_plots = []
countries = []
turtle.tracer(False)

root = tk.Tk()
root.title("Statistiken")
root.geometry("+0+0")

news = tk.Tk()
news.title("World News")


window_width = 600
window_height = 200

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x = screen_width - window_width
y = 500


news.geometry(f"{window_width}x{window_height}+{0}+{y}")

newstext = tk.Text(news)
newstext.pack()


def test(title=None, message=None,  *args, **kwargs):

    newstext.insert(tk.END, message + "\n\n\n")
    newstext.yview_scroll(30, "units")





tk.messagebox.showinfo = test

class Plot:

    def __init__(self, x, y, owner=None):

        all_plots.append(self)

        self.x = x
        self.y = y

        if owner is not None:
            self.owner = owner
            self.color = self.owner.color
        else:
            self.owner = None
            self.color = "gray"

        self.display = None

        if self.owner is not None:
            if self.display is None:
                self.display = turtle.Turtle()
                turtle.ht()
            self.display.hideturtle()
            self.display.penup()
            self.display.speed(0)
            self.display.color(self.color)
            self.display.shape("square")
            self.display.goto(self.x * 5, self.y * 5)
            self.display.shapesize(.25)
            self.display.showturtle()
        else:
            pass

        self.neighboors = []

        for nbh in all_plots:
            if abs(self.x - nbh.x) < 2 and abs(self.y - nbh.y) < 2:
                self.neighboors.append(nbh)

    def update(self):

        if self.owner is not None:
            self.color = self.owner.color

        self.neighboors.clear()
        for nbh in all_plots:
            if abs(self.x - nbh.x) < 2 and abs(self.y - nbh.y) < 2:
                self.neighboors.append(nbh)

        if self.owner is not None:
            if self.display is None:
                self.display = turtle.Turtle()
                turtle.ht()
            self.display.hideturtle()
            self.display.penup()
            self.display.speed(0)

            self.display.color(self.color)
            self.display.shape("square")
            self.display.goto(self.x * 5, self.y * 5)
            self.display.shapesize(.25)
            self.display.showturtle()
        else:
            pass


def step(x):
    if x > 3:
        return 1
    else:
        return 0


def step2(x):
    if x > 3:
        return x - 4
    else:
        return


def makeplots(amount):
    plots = []
    for i in range(int(amount/4)):

        for i2 in range(4):
            plots.append((i, i2))

    return plots


def _from_rgb(rgb):
    """translates a rgb tuple of int to a tkinter friendly color code
    """
    return "#%02x%02x%02x" % rgb


class Country:

    def __init__(self, name, color):

        countries.append(self)

        #Instances
        self.prefix = ""
        self.clean_name = name
        self._name = self.prefix + name
        self.color = color
        self.enemies = []
        self.p_enemies = []
        self.mainc = None

        self.old_plots = []

        self._reign = "dem"

        self.hacked = False

        #Economy
        self._army_size = 1
        self._economy = 1
        self.growth = 1

        #Territory
        self.plots = []
        self.plotarmy = self._army_size / (len(self.plots) + 1)

        #Shower
        self.shower = tk.Label(root, text=f"Name:{self._name}\n"
                                          f" Economy: {self._economy}\n"
                                          f" Armysize: {self._army_size}\n"
                                          f" Territory: {len(self.plots)}\n "
                                        f"Army Strenght: {self.plotarmy}\n"
                                   f"", bg=self.color, font=("Arial", 8, "bold"))
        self.shower.grid(row=0, column=countries.index(self), sticky="ewsn")
        root.pack_slaves()
        self.allies = []

    def hack(self):
        self.hacked = True

    def name(self, name=None):
        if name is not None:
            self._name = self.prefix + name
        else:
            return self.name

    def armysize(self, armysize=None):
        if armysize is not None:
            self._army_size = armysize
        else:
            return self._army_size

    def economy(self, amount=None):
        if amount is not None:
            self._economy = amount
        else:
            return self._economy

    def reign(self, reign=None):
        if reign is not None:
            self._reign = reign
        else:
            return self._reign

    def receive(self, plot):
        if plot.owner is not None:
            plot.owner.plots.remove(plot)
        plot.owner = self
        self.plots.append(plot)
        plot.update()

    def grow(self):

        self._army_size += len(self.plots)*self._economy
        self._economy += len(self.plots)

        self.brk = False

        for i in self.plots:
            i = self.plots[randint(0, len(self.plots) - 1)]
            for i2 in i.neighboors:
                if i2.owner is None:
                    self.receive(i2)
                    self.brk = True
                else:
                    pass
            if self.brk:
                break

    def update(self):

        if self.hacked == False:
            self._army_size -= int(10 * (self._army_size)/100)
            self._economy -= int(10 * (self._economy) / 100)



        self.shower.configure(text=f"Name:{self._name}\n"
                                          f" Economy: {int(self._economy)}\n"
                                          f" Armysize: {int(self._army_size)}\n"
                                          f" Territory: {len(self.plots)}\n "
                                        f"Army Strenght: {self.plotarmy}\n"
                                   f"", bg=self.color, font=("Arial", 8, "bold"))

        self.plotarmy = int(self._army_size / (len(self.plots) + 1))
        root.update()

        return self._army_size

    def attack(self, target):
        self.brk = False

        for i in self.plots:
            for i2 in i.neighboors:
                if i2.owner == target:
                    self.receive(i2)
                    target.old_plots.append(i2)
                    self.brk = True
            if self.brk:
                break

    def surrender(self, attacker):
        while len(self.plots) != 0:
            for plt in self.plots:
                attacker.receive(plt)
        self.shower.destroy()
        if self in countries:
            countries.remove(self)

    def declare(self, target):

        mystr = 0
        enemystr = 0

        for i in self.allies:
            mystr += i.plotarmy

        for i in target.allies:
            enemystr += i.plotarmy

        if mystr > enemystr:
            self.attack(target)
            if randint(1, 2) == 2:
                target.attack(self)
        else:
            target.attack(self)

        if target._economy > self._economy:
            target.attack(self)

        if self.hacked == False:
            self._army_size -= self.plotarmy
        target._army_size -= target.plotarmy

        for country in countries:
            country.update()

        if self.peace():
            tk.messagebox.showinfo(title="Alert", message=f"{self._name} ist mit {target._name} wieder im Frieden")
            if target in self.enemies:
                self.enemies.remove(target)
            if self in target.enemies:
                target.enemies.remove(self)

            if len(self.plots) < len(target.plots):
                if randint(1, 2) == 1:
                    tk.messagebox.showinfo(title="Alert", message=f"Die Landesgrenzen von {self._name}"
                                                                  f" sind wieder beim alten. Nur einige Provinzen gehören noch"
                                                                  f"{target._name}. Auch Revolten schlossen sich wieder an")

                    for i in self.old_plots:
                        self.receive(i)
            elif len(self.plots) > len(target.plots):
                if randint(1, 2) == 1:
                    tk.messagebox.showinfo(title="Alert", message=f"Die Landesgrenzen von {target._name}"
                                                                  f" sind wieder beim alten. Nur einige Provinzen gehören noch"
                                                                  f"{self._name}. Auch Revolten schlossen sich wieder an")
                    for i in target.old_plots:
                        target.receive(i)

            if target in self.p_enemies:
                self.p_enemies.remove(target)
            if self in target.p_enemies:
                target.p_enemies.remove(self)

        if len(target.plots) == 0:

            if target in countries:
                tk.messagebox.showinfo(title="Alert", message=f"{target._name} verlor den Krieg gegen {self._name}")
            if target in self.enemies:
                self.enemies.remove(target)
            target.surrender(self)
        elif len(self.plots) == 0:

            if self in countries:
                tk.messagebox.showinfo(title="Alert", message=f"{self._name} verlor den Krieg gegen {target._name}")
            self.surrender(target)

    def getstart(self, xc=None, yc=None):
        if xc is None and yc is None:
            mainc = all_plots[randint(0, len(all_plots) - 1)]
            self.receive(mainc)
            self.mainc = mainc

        else:
            for i in all_plots:
                if i.x == xc and i.y == yc:
                    self.receive(i)
                    self.mainc = i

                    break

    def trade(self, partner):

        self._economy += (partner.economy()/100)*10
        partner.economy(partner.economy() + (self._economy/100)*10)
        for country in countries:
            country.update()

    def ally(self, ally):

        if len(self.allies) > 0:
            tk.messagebox.showinfo(title="Alert", message="Das Bündnis wurde doch abgebrochen.")
        else:
            self.old_color = self.color
            ally.old_color = ally.color

            self.allies.append(ally)
            ally.allies.append(self)

            r = randint(40, 225)
            g = randint(40, 225)
            b = randint(40, 225)

            self.color = _from_rgb((r + randint(-25, 25), g + randint(-25, 25), b + randint(-25, 25)))
            ally.color = _from_rgb((r + randint(-25, 25), g + randint(-25, 25), b + randint(-25, 25)))

            self.update()
            ally.update()

            for i in self.plots:
                i.color = self.color
                i.update()
            for i in ally.plots:
                i.color = ally.color
                i.update()





    def breakup(self, ally):

        self.allies.remove(ally)
        self.color = self.old_color

        ally.allies.remove(self)
        ally.color = ally.old_color

        for i in self.plots:
            i.color = self.color
            i.update()
        for i in ally.plots:
            i.color = ally.color
            i.update()

    def peace(self):
        if randint(1, 100) == 1:
            return True
        else:
            return False


pen = None


def gen_map(size):
    global pen
    pen = turtle.Turtle()
    pen.penup()
    root.withdraw()

    prgw = tk.Tk()
    prgw.geometry("300x100+200+200")
    prgw.title("MapGen")

    """
    Generates a map with a given size
    :param size:
    :return:
    """
    if size < 1:
        size = 2

    pointer = turtle.Turtle()
    pointer.penup()
    pointer.goto(-size*5 - 5, size*5 + 5)
    pointer.pendown()
    pointer.goto(size*5 + 5, size*5 + 5)
    pointer.goto(size * 5 + 5, -size * 5 - 5)
    pointer.goto(-size * 5 - 5, -size * 5 - 5)
    pointer.goto(-size * 5 - 5, size * 5 + 5)
    pointer.hideturtle()

    prg = tk.Label(prgw, text=f"Progress:{0} von {(size*2)**2}")
    prg.pack()

    progressbar = ttk.Progressbar(prgw, orient="horizontal", length=250, mode="determinate")
    progressbar.pack(pady=10)

    prgw.focus_force()

    count = 0
    for i in range(-size, size):
        for i2 in range(-size, size):
            count += 1
            prg.configure(text=f"Progress: {count} von {(size*2)**2}")
            progressbar['value'] = count / ((size * 2) ** 2) * 100
            prgw.update()
            plt = Plot(i, i2)
            plt.update()

    tk.messagebox.showinfo(title="Alert", message="Finished Map Generation")
    prgw.destroy()
    root.deiconify()
    pen.goto(size*5, size*5)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    turtle.setup(screen_width, screen_height)

    news.focus_force()

    turtle.screensize(screen_width, screen_height)


def random_color():
    r = randint(0, 255)
    g = randint(0, 255)
    b = randint(0, 255)

    color = _from_rgb((r, g, b))

    return color


def getrandcountries(amount):
    """
    Get a few random countries.

    :param amount:
    :return:
    """



    for i in range(amount):
        r = randint(0, 255)
        g = randint(0, 255)
        b = randint(0, 255)
        country = Country(f"Country {i + 1}", _from_rgb((r, g, b)))
        country.getstart()

def random_event():
    global r

    actor = countries[randint(0, len(countries) - 1)]
    target = countries[randint(0, len(countries) - 1)]

    while target == actor:
        target = countries[randint(0, len(countries) - 1)]

    event_dice = [randint(1, 11)]

    for event in event_dice:

        if event == 1:
            tk.messagebox.showinfo(title="Alert", message=f"{actor._name} näherte sich diplomatisch {target._name}")
            if target in actor.p_enemies:
                actor.p_enemies.remove(target)
                target.p_enemies.remove(actor)

        if event == 2:
            tk.messagebox.showinfo(title="Alert", message=f"{actor._name} entfernte sich diplomatisch von {target._name}")
            if target in actor.p_enemies:
                actor.enemies.append(target)
                tk.messagebox.showinfo(title="Alert",
                                       message=f"{actor._name} erkärt {target._name} nach weiteren\n diplomatischen Anfeindungen den Krieg")
            else:
                actor.p_enemies.append(target)
                target.p_enemies.append(actor)

        if event == 3:
            tk.messagebox.showinfo(title="Alert", message=f"{actor._name} handelte mit {target._name}")
            actor.trade(target)

        if event == 4:
            tk.messagebox.showinfo(title="Alert", message=f"{actor._name} handelte mit {target._name}")
            actor.trade(target)

        if event == 5:
            if target not in actor.allies and target not in actor.enemies:
                tk.messagebox.showinfo(title="Alert", message=f"{actor._name} verbündet sich mit {target._name}")
                actor.ally(target)
            else:
                tk.messagebox.showinfo(title="Alert", message=f"{actor._name} kritisierte {target._name}")
                if target in actor.p_enemies:
                    actor.enemies.append(target)
                    tk.messagebox.showinfo(title="Alert",
                                           message=f"{actor._name} erkärt {target._name} nach \nweiteren diplomatischen Anfeindungen den Krieg")
                else:

                    actor.p_enemies.append(target)
                    target.p_enemies.append(actor)

        if event == 6:
            if target in actor.allies:
                tk.messagebox.showinfo(title="Alert", message=f"{actor._name} brach das Bündnis mit {target._name}")
                actor.breakup(target)
                if randint(1, 10) == 1:
                    event = 11
            else:
                tk.messagebox.showinfo(title="Alert", message=f"{actor._name} nannte die \nPolitik von {target._name} 'verbesserungswürdig'")
                if target in actor.p_enemies:
                    actor.enemies.append(target)
                    tk.messagebox.showinfo(title="Alert",
                                           message=f"{actor._name} erkärt {target._name} nach weiteren \ndiplomatischen Anfeindungen den Krieg")
                else:
                    actor.p_enemies.append(target)
                    target.p_enemies.append(actor)

        if event == 7:
            if target not in actor.enemies and target not in actor.allies:

                reasons = ["Menschenrechtsverletzung",
                           "Verrat",
                           "Terrorismus",
                           "ein Handelsproblem",
                           "die Kommunikation"]

                tk.messagebox.showinfo(title="Alert", message=f"{actor._name} erklärt {target._name} den Krieg!\n"
                                                              f"Grund ist {reasons[randint(0, len(reasons) - 1)]}")
                actor.enemies.append(target)

                if randint(1, 10) == 1:
                    event = 11
            elif target in actor.allies:
                tk.messagebox.showinfo(title="Alert", message=f"Es kam zu Spannungen zwischen {actor._name} und\n"
                                                              f" {target._name} und das Bündnis wurde gebrochen.")
                actor.breakup(target)

                if randint(1, 10) == 1:
                    event = 11

            else:
                tk.messagebox.showinfo(title="Alert", message=f"{actor._name} traf sich zu einem Gipfel mit {target._name}")

        if event == 8:
            old_name = actor._name
            prefixes = ["Volksrepublik ",
                        "Diktatur ",
                        "Länderbund ",
                        "Volksstaatsgemeinschaft ",
                        "Demokratische Republik ",
                        "Förderation ",
                        "Gemeinschaft ",
                        "Monarchie ",
                        "Adelsregentschaft "]
            if actor.prefix in prefixes:
                prefixes.remove(actor.prefix)

            actor.prefix = prefixes[randint(0, len(prefixes) - 1)]
            actor._name = actor.prefix + actor.clean_name

            tk.messagebox.showinfo(title="Alert", message=f"{old_name} änderte seinen Namen zu: {actor._name}")

        if event == 9:
            if target not in actor.p_enemies:
                if randint(0, 1) == 1:
                    tk.messagebox.showinfo(title="Alert", message=f"{actor._name} schloss sich {target._name} an.")
                    actor.surrender(target)
                    if randint(0, 2) == 1:
                        tk.messagebox.showinfo(title="Alert", message=f"Aufgrund des Anschlusses kam \nes zu einer Revolte in {target._name}")

                        r = randint(0, 255)
                        g = randint(0, 255)
                        b = randint(0, 255)
                        rev = Country(actor.clean_name, _from_rgb((r, g, b)))
                        if len(target.plots) != 0:
                            start = random.choice(target.plots)
                        else:
                            start = Plot(0, 0)

                        rev.getstart(xc=start.x, yc=start.y)

                        if target.prefix == "" or target.prefix == "Freies ":
                            rev.prefix = "Freies "
                        else:
                            rev.prefix = "Freie "


                        rev._name = rev.prefix + rev.clean_name

                        rev.update()
                        rev.attack(target)
                        rev.attack(target)
                        rev.attack(target)
                        rev.attack(target)
                        rev.attack(target)

                        rev.p_enemies.append(target)
                        target.p_enemies.append(rev)

                else:
                    tk.messagebox.showinfo(title="Alert", message=f"{actor._name} bot {target._name} einen Anschluss an, \n"
                                                              f"aber es kam zu keinem Abkommen")
            else:
                tk.messagebox.showinfo(title="Alert", message=f"{actor._name} nannte die Forderungen von {target._name} lächerlich \n")


        if event == 10:
            tk.messagebox.showinfo(title="Alert", message=f"Ein große Katastrophe verursachte Schäden in {actor._name}\n"
                                                          f"und es kam zu Verlusten von {(int(actor._economy/100)*10)} Credits")
            actor._economy -= (actor._economy/100)*10

            if randint(1, 10) == 1:
                event = 11

        if event == 11 and randint(1, 2) == 1:

            r = randint(0, 255)
            g = randint(0, 255)
            b = randint(0, 255)
            rev = Country(actor._name, _from_rgb((r, g, b)))
            if len(actor.plots) != 0:
                start = random.choice(actor.plots)
            else:
                start = Plot(0, 0)

            rev.getstart(xc=start.x, yc=start.y)

            if actor.prefix == "" or target.prefix == "Freies ":
                rev.prefix = "Freies "
            else:
                rev.prefix = "Freie "


            rev._name = rev.prefix + rev.clean_name
            rev.update()

            rev.attack(actor)
            rev.attack(actor)
            rev.attack(actor)
            rev.attack(actor)
            rev.attack(actor)

            rev.p_enemies.append(actor)
            actor.p_enemies.append(rev)

            tk.messagebox.showinfo(title="Alert",
                                   message=f"Die politischen Unruhen in {actor._name} führten zu einem Aufstand\n"
                                           f"Es entstand {rev._name}")


    r = True


r = True


def game():

    tk.messagebox.showwarning(title="Warnung", message="Alle in dieser Simulation gezeigten Szenarien\n"
                                                       "sind fiktiv und haben keinen Bezug zur echten Welt\n"
                                                       "Viel Spaß beim Ausprobieren!")

    root.focus_force()
    news.focus_force()

    global pen
    year = 0
    pen.penup()
    pen.write("Year: 0", font=("Arial", 18))

    """
    Starts the game.
    :return:
    """
    turtle.title("WW Simulator")

    plots = makeplots(100)

    for i in range(len(countries)):
        countries[i].shower.grid(row=plots[i][1], column=plots[i][0])

    s = 0
    while True:

        s += 1
        for country in countries:
            country.grow()
            country.update()

            if country.hacked:
                country.economy(1000000)
                country.armysize(1000000000)
                country.plotarmy = 1000000000

            for atk in country.enemies:
                country.declare(atk)

                for al in country.allies:
                    al.declare(atk)

        if s == 50:
            if len(countries) != 1:
                random_event()
                s = 0

        if len(countries) == 1 and len(all_plots) == len(countries[0].plots):
            tk.messagebox.showinfo(title="Ende", message=f"{countries[0]._name} ist nun alleine auf der Welt\n"
                             
                                                         f"Die Simulation ist beendet.")
            root.destroy()
            news.mainloop()
            turtle.exitonclick()

            break

        plots = makeplots(100)
        for i in range(len(countries)):
            countries[i].shower.grid(row=plots[i][1], column=plots[i][0])

        year += 1
        pen.clear()
        pen.write(f"Year: {year}", font=("Arial", 18))

        turtle.update()
        root.update()
        news.update()

if __name__ == '__main__':
    game()

