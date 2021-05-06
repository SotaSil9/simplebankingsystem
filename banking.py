import random
import sqlite3


class BankingSystem:
    conn = sqlite3.connect('card.s3db')  # creating new table with demand params and check if not exist
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS card(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number TEXT,
    pin TEXT,
    balance INTEGER DEFAULT 0);
    """)
    conn.commit()

    def menu(self):  # authorisation menu
        while True:
            call = int(input(f'1. Create an account\n2. Log into account\n0. Exit\n'))
            if call == 1:
                self.create_account()
            elif call == 2:
                self.log_in()
            elif call == 0:
                print("\nBye!")
                self.conn.close()
                quit()
            else:
                print("Unknown operation")

    def create_account(self):  # generate credit card number using luhn algoritm 
        account_identifier_user = random.randint(100000000, 999999999)
        account_identifier = "400000" + str(account_identifier_user)
        card_number = int(account_identifier + str(self.luhn(account_identifier)))
        pin = random.randint(1000, 9999)
        self.cur.execute(f"INSERT INTO card (number, pin) VALUES ({card_number}, {pin});")
        self.conn.commit()
        print(f"\nYour card has been created\nYour card number:\n{card_number}\nYour card PIN:\n{pin}\n")
        self.menu()

    def log_in(self):  # log-in menu checking log/pass into sql database
        login_name = int(input("Enter your card number:\n"))
        pin_name = int(input("Enter your PIN:\n"))
        self.cur.execute(f"SELECT * FROM card WHERE number={login_name} AND pin={pin_name}")
        if bool(self.cur.fetchone()) is not False:
            print("\nYou have successfully logged in!\n")
            self.inner_menu(login_name, pin_name)
        else:
            print("\nWrong card number or PIN\n")
            self.menu()

    def inner_menu(self, login_name, pin_name):
        while True:
            call = int(input(f'1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit\n'))
            if call == 1:
                print(f'Balance: {self.balance(login_name)}')
            elif call == 2:
                self.add_income(login_name, pin_name)
            elif call == 3:
                self.do_transfer(login_name, pin_name)
            elif call == 4:
                self.close_account(login_name)
            elif call == 5:
                self.menu()
            elif call == 0:
                print("\nBye!")
                self.conn.close()
                quit()
            else:
                print("Unknown operation")

    def add_income(self, login_name, pin_name):  # add money to deposit
        income = int(input('\nEnter income:\n'))
        income += self.balance(login_name)
        self.cur.execute(f'UPDATE card SET balance={income} WHERE number={login_name};')
        self.conn.commit()
        print('Income was added!\n')
        self.inner_menu(login_name, pin_name)

    def balance(self, login_name):  # current balance to simplify cod in other functions
        self.cur.execute(f"SELECT balance FROM card WHERE number={login_name}")
        balance = self.cur.fetchone()[0]
        self.conn.commit()
        return balance

    def do_transfer(self, login_name, pin_name):  # transfer money to another account(with base check and luhn check for existing number)
        card_number = int(input("\nTransfer\nEnter card number:\n"))
        if self.luhn_check(card_number) is False:
            print("Probably you made a mistake in the card number. Please try again!\n")
            self.inner_menu(login_name, pin_name)
        self.cur.execute(f"SELECT * FROM card WHERE number={card_number}")
        if bool(self.cur.fetchone()) is False:
            print('Such a card does not exist\n')
            self.inner_menu(login_name, pin_name)
        transfer = int(input('Enter how much money you want to transfer:\n'))
        transfer_from = self.balance(login_name) - transfer
        transfer_to = self.balance(card_number) + transfer
        if transfer_from < 0:
            print('Not enough money!\n')
            self.inner_menu(login_name, pin_name)
        self.cur.execute(f'UPDATE card SET balance={transfer_from} WHERE number={login_name};')
        self.cur.execute(f'UPDATE card SET balance={transfer_to} WHERE number={card_number}')
        self.conn.commit()
        print('Success!\n')

    def close_account(self, login_name):  # delete account from the base
        self.cur.execute(f'DELETE FROM card WHERE number={login_name}')
        self.conn.commit()
        print('\nThe account has been closed!\n')
        self.menu()

    @staticmethod
    def luhn_check(card_number):  # if number is possible
        last_number = str(card_number)[-1]
        card_identifier = str(card_number)[0:-1]
        if BankingSystem().luhn(card_identifier) == int(last_number):
            return True
        else:
            return False

    @staticmethod
    def luhn(account_identifier):  # last digit via luhn algoritm
        n = 1
        sum = 0
        for i in account_identifier:
            i = int(i)
            if n % 2 != 0:
                i *= 2
            if i > 9:
                i -= 9
            sum += i
            n += 1
        last_digit = 10 - sum % 10
        if last_digit == 10:
            last_digit = 0
        return last_digit


BankingSystem().menu()

