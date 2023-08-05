import subprocess
import pygame, sys
from pygame.locals import *
import random, time
import os
import csv
import pandas as pd
from datetime import datetime
import spwf

python_path = sys.executable 

participant_number = spwf.participant_number

filename = os.path.join(spwf.folder_name, f"{participant_number} - RT Score.csv")
filename2 = os.path.join(spwf.folder_name, f"{participant_number} - RT Reaction Times.csv")
filename3 = os.path.join(spwf.folder_name, f"{participant_number} - Combined Reaction Times.csv")
filename4 = os.path.join(spwf.folder_name, f"{participant_number} - Combined Scores.csv")

now = datetime.now()

date_time_string = now.strftime("%d-%m-%y")
outputtime = now.strftime("%H:%M:%S")

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = (
    pygame.display.Info().current_w,
    pygame.display.Info().current_h,
)

pygame.font.init()

FONT = pygame.font.Font(None, 100)

size = [SCREEN_WIDTH, SCREEN_HEIGHT - 50]
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)

screen.fill(WHITE)

pygame.display.set_caption("Task")

def show_welcome_screen():
    pygame.font.init()

    os.environ["SDL_VIDEO_CENTERED"] = "1"

    score = 0

    # font
    font = pygame.font.Font(None, 32)

    order = 1

    start_time = pygame.time.get_ticks()

    Game_Running = True

    starterRT = time.time()

    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
    screen.fill(WHITE)
    pygame.display.set_caption("Welcome to the Task")
    font = pygame.font.Font(None, 60)
    text = font.render("Welcome to the Task", True, BLACK)
    text_rect = text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
    screen.blit(text, text_rect)

    timeout = 3

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
        # Subtract the elapsed time from 60 to get the remaining time
        remaining_time = timeout - elapsed_time
        if remaining_time < 0:
            running = False
            remaining_time = 0

        # Create a text surface with the remaining time
        text2 = font.render(str(remaining_time), True, BLACK)
        text2_rect = text2.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 200))

        # Fill the screen with white
        screen.fill(WHITE)

        text = font.render("Welcome to the Task!", True, BLACK)
        text_rect = text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))

        screen.blit(text2, text2_rect)
        screen.blit(text, text_rect)

        # Update the display
        pygame.display.update()

    pygame.display.update()
        
def intro():
    os.environ['SDL_VIDEO_CENTERED'] = '1'

    score = 0
    
    #random_number = random.randint(11111,99999)

    pygame.init()

    SCREEN_WIDTH, SCREEN_HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h

    pygame.font.init()

    FONT = pygame.font.Font(None, 100)

    size = [SCREEN_WIDTH,SCREEN_HEIGHT-50]
    #SCREEN_WIDTH = 1000
    #SCREEN_HEIGHT = 1000
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    screen = pygame.display.set_mode(size, pygame.RESIZABLE)

    screen.fill(WHITE)

    pygame.display.set_caption("Task")

    # Loop until the user clicks the close button.
    done = False

    clock = pygame.time.Clock()


    # font
    font = pygame.font.Font(None, 32)

    display_instructions = True
    instruction_page = 1

    DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    
    #DISPLAYSURF.fill(WHITE)

    order = random.randint(1,2)

    Game_Running = True

    starterRT = time.time()

    timer = random.randint(1,5)

    if timer == 1:
     wait = 1100
    if timer == 2:
     wait = 1200
    if timer == 3:
     wait = 1300         
    if timer == 4:
     wait = 1400
    if timer == 5:
     wait = 1500

    while Game_Running:
        # Set the screen background
        screen.fill(WHITE)
        
        if order == 1:
            ImageSample = pygame.image.load('asterisk.png')
        else:
            ImageSample = pygame.image.load('circle.jpg')

        ImageSample_rect = ImageSample.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        screen.blit(ImageSample, ImageSample_rect)
        
        text = font.render("You will be presented with a symbol. If you see the symbol 'O' press the F key, if you see the symbol '*' press the J key.", True, BLACK)
        text_rect = text.get_rect(center=(SCREEN_WIDTH/2,40))
        screen.blit(text, text_rect)
        
        text = font.render("Let's practice this now, take your time in understanding the task", True, BLACK)
        text_rect = text.get_rect(center=(SCREEN_WIDTH/2,120))
        screen.blit(text, text_rect)
        
        text = font.render("", True, RED)
        text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2+350))
        screen.blit(text, text_rect)

        incorrectinterval = pygame.image.load("redcross.png")
        incorrectintervaldimensions = incorrectinterval.get_rect(center=screen.get_rect().center)
        
        correctinterval = pygame.image.load("greentick.png")
        correctintervaldimensions = correctinterval.get_rect(center=screen.get_rect().center)        
                
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Game_Running = False
            pygame.event.pump()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f and order == 2:
                    endRT = time.time()
                    print("RT is: ", 60*(endRT - starterRT))
                    screen.fill(WHITE)
                    score += 1
                    screen.blit(correctinterval, correctintervaldimensions)
                    pygame.time.wait(1000)
                    pygame.display.update()
                    pygame.time.wait(1000)
                    Game_Running = False
                    
                elif event.key == pygame.K_j and order == 1:
                    endRT = time.time()
                    print("RT is: ", 60*(endRT - starterRT))
                    screen.fill(WHITE)
                    score += 1
                    screen.blit(correctinterval, correctintervaldimensions)
                    pygame.time.wait(1000)
                    pygame.display.update()
                    pygame.time.wait(1000)
                    Game_Running = False
                    
                else:  # if incorrect key was pressed
                    endRT = time.time()
                    print("RT is: ", 60*(endRT - starterRT))
                    screen.fill(WHITE)
                    screen.blit(incorrectinterval, incorrectintervaldimensions)
                    pygame.time.wait(1000)
                    pygame.time.wait(1000)
                    Game_Running = False

        pygame.display.update()
        pygame.time.delay(wait)

    #trialcounter += 1
    print("Score", score)
    print("Trial Count", trialcounter)

def practice():

    os.environ["SDL_VIDEO_CENTERED"] = "1"

    score = 0

    # Loop until the user clicks the close button.
    done = False

    clock = pygame.time.Clock()


    # font
    font = pygame.font.Font(None, 32)

    display_instructions = True
    instruction_page = 1

    DISPLAYSURF = pygame.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN
    )

    DISPLAYSURF.fill(WHITE)

    order = random.randint(1, 2)

    Game_Running = True

    starterRT = time.time()
            
    timer = random.randint(1,5)

    if timer == 1:
     wait = 1100
    if timer == 2:
     wait = 1200
    if timer == 3:
     wait = 1300         
    if timer == 4:
     wait = 1400
    if timer == 5:
     wait = 1500

    while Game_Running:

        DISPLAYSURF.fill(WHITE)

        if order == 2:
            ImageSample = pygame.image.load("asterisk.png")
            
        else:
            ImageSample = pygame.image.load("circle.jpg")

        ImageSample_rect = ImageSample.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50))
        screen.blit(ImageSample, ImageSample_rect)

        incorrectinterval = pygame.image.load("redcross.png")
        incorrectintervaldimensions = incorrectinterval.get_rect(center=screen.get_rect().center)

        correctinterval = pygame.image.load("greentick.png")
        correctintervaldimensions = correctinterval.get_rect(center=screen.get_rect().center)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Game_Running = False
            pygame.event.pump()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f and order == 1:
                    endRT = time.time()
                    RT = endRT - starterRT
                    screen.fill(WHITE)
                    score += 1
                    screen.blit(correctinterval, correctintervaldimensions)
                    pygame.time.wait(500)
                    pygame.display.update()
                    pygame.time.wait(500)
                    Game_Running = False

                elif event.key == pygame.K_j and order == 2:
                    endRT = time.time()
                    RT = endRT - starterRT
                    screen.fill(WHITE)
                    score += 1
                    screen.blit(correctinterval, correctintervaldimensions)
                    pygame.time.wait(500)
                    pygame.display.update()
                    pygame.time.wait(500)
                    Game_Running = False

                else: 
                    endRT = time.time()
                    RT = endRT - starterRT
                    screen.fill(WHITE)
                    screen.blit(incorrectinterval, incorrectintervaldimensions)
                    pygame.time.wait(500)
                    pygame.display.update()
                    pygame.time.wait(500)
                    Game_Running = False

        pygame.display.flip()
        pygame.time.delay(1000)

def exitscreen():
    os.environ["SDL_VIDEO_CENTERED"] = "1"

    df = pd.read_csv(filename2, usecols=[2], header=None)
    mean = df.mean().values[0]

    accuracydf = pd.read_csv(filename, usecols=[2], header=None)
    accuracydf = accuracydf.round(1)

    counter = accuracydf.count().values[0]
    formatted_num = "{:.2f}".format(mean)
    #print(formatted_num)


    totalscore = accuracydf.sum().values[0]

    #print(totalscore,counter)
    finalscore = totalscore / counter * 100
    #print("Percentage" , finalscore)

    formatted_acc = "{:.1f}".format(finalscore)
    #print(formatted_acc)
    # font
    font = pygame.font.Font(None, 32)

    DISPLAYSURF = pygame.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE
    )

    DISPLAYSURF.fill(WHITE)

    text = font.render("The task is now complete, thank you!", True, BLACK)
    text_rect = text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 100))
    screen.blit(text, text_rect)

    text = font.render(
        "Your average reaction time is: " + str(formatted_num) + " seconds", True, BLACK
    )
    text_rect = text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
    screen.blit(text, text_rect)

    text = font.render(
        "Your combined accuracy rate is: " + str(formatted_acc) + "%", True, BLACK
    )
    text_rect = text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50))
    screen.blit(text, text_rect)

    pygame.display.update()
    # pygame.time.delay(500)
    pygame.time.delay(10000)
    
def task():
    timer = random.randint(1,5)

    if timer == 1:
     wait = 1100
    if timer == 2:
     wait = 1200
    if timer == 3:
     wait = 1300         
    if timer == 4:
     wait = 1400
    if timer == 5:
     wait = 1500
     
    os.environ["SDL_VIDEO_CENTERED"] = "1"

    score = 0

    # Loop until the user clicks the close button.
    done = False

    clock = pygame.time.Clock()

    # Starting position of the silhouette
    rect_x = 50
    rect_y = 50

    # Speed and direction of rectangle
    rect_change_x = 5
    rect_change_y = 5

    # font
    font = pygame.font.Font(None, 32)

    display_instructions = True
    instruction_page = 1

    DISPLAYSURF = pygame.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN
    )

    # DISPLAYSURF.fill(WHITE)

    order = random.randint(1, 2)
    print(order)


    Game_Running = True

    starterRT = time.time()

    while Game_Running:
        # Set the screen background
        screen.fill(WHITE)

        if order == 2:
            ImageSample = pygame.image.load("asterisk.png")
            
        else:
            ImageSample = pygame.image.load("circle.jpg")

        ImageSample_rect = ImageSample.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50))
        screen.blit(ImageSample, ImageSample_rect)

        incorrectinterval = pygame.image.load("redcross.png")
        incorrectintervaldimensions = incorrectinterval.get_rect(center=screen.get_rect().center)

        correctinterval = pygame.image.load("greentick.png")
        correctintervaldimensions = correctinterval.get_rect(center=screen.get_rect().center)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Game_Running = False
            pygame.event.pump()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f and order == 1:
                    endRT = time.time()
                    RT = endRT - starterRT
                    score += 1
                    pygame.time.wait(1000)
                    Game_Running = False

                elif event.key == pygame.K_j and order == 2:
                    endRT = time.time()
                    RT = endRT - starterRT
                    score += 1
                    pygame.time.wait(1000)
                    Game_Running = False

                else:  # if incorrect key was pressed
                    endRT = time.time()
                    RT = endRT - starterRT
                    pygame.time.wait(1000)
                    Game_Running = False

        pygame.display.update()
        pygame.time.delay(wait)

    with open(filename, mode="a+") as file:
        file.write(f"{date_time_string}, {count}, {score}, Reaction Time\n")

    with open(filename2, mode="a+") as file:
        file.write(f"{date_time_string}, {count}, {RT}, Reaction Time\n")

    with open(filename4, mode="a+") as file:
        file.write(f"{date_time_string}, {count}, {score}, Reaction Time\n")

    with open(filename3, mode="a+") as file:
        file.write(f"{date_time_string}, {count}, {RT}, Reaction Time\n")

def exitscreen():
    os.environ["SDL_VIDEO_CENTERED"] = "1"

    df = pd.read_csv(filename2, usecols=[2], header=None)
    mean = df.mean().values[0]

    accuracydf = pd.read_csv(filename, usecols=[2], header=None)
    accuracydf = accuracydf.round(1)

    counter = accuracydf.count().values[0]
    formatted_num = "{:.2f}".format(mean)
    #print(formatted_num)


    totalscore = accuracydf.sum().values[0]

    #print(totalscore,counter)
    finalscore = totalscore / counter * 100
    #print("Percentage" , finalscore)

    formatted_acc = "{:.1f}".format(finalscore)
    #print(formatted_acc)
    # font
    font = pygame.font.Font(None, 32)

    DISPLAYSURF = pygame.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE
    )

    DISPLAYSURF.fill(WHITE)

    text = font.render("The task is now complete, thank you!", True, BLACK)
    text_rect = text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 100))
    screen.blit(text, text_rect)

    text = font.render(
        "Your average reaction time is: " + str(formatted_num) + " seconds", True, BLACK
    )
    text_rect = text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
    screen.blit(text, text_rect)

    text = font.render(
        "Your combined accuracy rate is: " + str(formatted_acc) + "%", True, BLACK
    )
    text_rect = text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50))
    screen.blit(text, text_rect)

    pygame.display.update()
    # pygame.time.delay(500)
    pygame.time.delay(10000)
    
def sysexit():
    pygame.quit()
    sys.exit()

count_file = 'RT count.txt'

if os.path.exists(count_file):
    with open(count_file, 'r') as f:
        count = int(f.read())
else:
    count = 0

count += 1

with open(count_file, 'w') as f:
    f.write(str(count))

trialcounter = 0

show_welcome_screen()
intro()

for i in range(0,10):
    practice()
    trialcounter += 1

for i in range(0,40):
    task()
    trialcounter += 1
    '''

8-10 trials, non-recorded, omit data, 40 recorded.
 feedback in the first 8-10, not in the recorded'''

exitscreen()
import Export
sysexit()
