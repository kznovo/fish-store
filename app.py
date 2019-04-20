"""魚屋ゲーム"""

import random
import sys
import copy
import datetime
from typing import Dict, Union, List, Optional, Any
from data import fish, harbors


class Item:
    def __init__(
        self, name: str, purchace_price: int, expires_at: datetime.date
    ) -> None:
        self.name = name
        self.purchace_price = purchace_price
        self.expires_at = expires_at

    def __repr__(self):
        return f"{self.name} - ¥{self.purchace_price} - 売り期限：{self.expires_at}"


Inventory = Dict[Item, int]


class Store:
    def __init__(
        self,
        initial_balance: int = random.randint(500, 5000),
        initial_inventory: Inventory = {},
    ):
        self.balance = initial_balance
        self.inventory = initial_inventory

    def buy(self, item: Item, amount: int) -> None:
        self.inventory.update({item: amount})
        self.balance -= item.purchace_price * amount

    def sell(self, item: Item, amount: int, sell_price: int) -> None:
        self.inventory[item] -= amount
        self.balance += sell_price * amount
        if self.inventory[item] == 0:
            del self.inventory[item]

    def clean_inventory(self, date: datetime.date) -> None:
        _inventory = {}  # type: Inventory
        for item, amount in self.inventory.items():
            if item.expires_at < date:
                print(f"[処分] {item} {amount}尾")
            else:
                _inventory.update({item: amount})
        self.inventory = _inventory


def generate_fish(date: datetime.date) -> Item:
    price = random.randint(100, 5000)
    caught_at = random.choice(harbors)
    name = random.choice(fish)
    expires_at = date + datetime.timedelta(days=random.randint(1, 3))
    return Item(f"{caught_at}産 {name}", price, expires_at)


def main() -> None:
    s = Store()
    initial_balance = s.balance
    day = datetime.date.today()
    available_actions = [
        "1. 在庫をみる",
        "2. 商品を仕入れる",
        "3. 商品を売る",
        "4. 翌日にいく（販管費¥500円が差し引かれます）",
    ]
    todays_actions = copy.deepcopy(available_actions)
    nl = "\n"

    while True:
        option_str = f"{nl}{day}{nl}残高：¥{s.balance} {'+' if s.balance >= initial_balance else ''}{round((s.balance / initial_balance - 1) * 100, 3)}%{nl}=====何をしますか？====={nl}{nl.join(todays_actions)}{nl}>"
        try:
            action = int(input(option_str))
        except:
            print("数字を入力してください")
            continue

        if action == 1:
            print(s.inventory)

        elif action == 2:
            if "2. 商品を仕入れる" not in todays_actions:
                continue

            fish_on_sale = [generate_fish(day) for _ in range(3)]
            for i, f in enumerate(fish_on_sale, 1):
                print(i, f)
            print(4, "何も買わない")

            try:
                buy_ix = int(input(f"どの商品を買いますか？{nl}>")) - 1
            except:
                print("数字を入力してください")
                continue

            if buy_ix < 0 or buy_ix >= 3:
                continue
            buy_amount = int(input(f"何尾買いますか？{nl}>"))
            if not isinstance(buy_amount, int):
                continue
            s.buy(fish_on_sale[buy_ix], buy_amount)
            print()
            print(f"在庫：{s.inventory}")
            print(f"残金：¥{s.balance}")
            todays_actions.remove("2. 商品を仕入れる")

        elif action == 3:
            if "3. 商品を売る" not in todays_actions:
                continue
            market = [
                {
                    "item": item,
                    "selling_price": int(
                        item.purchace_price * random.uniform(0.9, 1.3)
                    ),
                    "amount": amount,
                }
                for item, amount in s.inventory.items()
            ]
            for i, deal in enumerate(market, 1):
                print(
                    f"{i} {deal['item']} - 売値：{deal['selling_price']}円 - 残{deal['amount']}尾"
                )

            try:
                sell_ix = int(input("どの商品を売りますか？")) - 1
            except:
                print("数字を入力してください")
                continue

            if sell_ix < 0 or sell_ix > len(market) - 1:
                todays_actions.remove("3. 商品を売る")
                continue
            sell_item = market[sell_ix]

            try:
                sell_amount = min(int(input(f"何尾売りますか？{nl}>")), sell_item["amount"])
            except:
                print("数字を入力してください")
                continue

            s.sell(sell_item["item"], sell_amount, sell_item["selling_price"])
            todays_actions.remove("3. 商品を売る")

        elif action == 4:
            day += datetime.timedelta(days=1)
            s.clean_inventory(day)
            s.balance -= 500
            todays_actions = copy.deepcopy(available_actions)

        if s.balance < 0:
            print(f"GAME OVER: 借金¥{s.balance}")
            sys.exit(1)


if __name__ == "__main__":
    main()
