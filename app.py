"""魚屋ゲーム"""

import random
import copy
import datetime
from typing import Dict, Union, List, Optional, Any, Optional
from data import fish, harbors


class Item:
    """商品クラス
    名前、仕入れ値、賞味期限、売値を管理する。
    """

    def __init__(
        self, name: str, purchace_price: int, expires_at: datetime.date
    ) -> None:
        self.name = name
        self.purchace_price = purchace_price
        self.expires_at = expires_at

    def __repr__(self):
        return f"{self.name} - ¥{self.purchace_price} - 売り期限：{self.expires_at}"


# 店舗で管理する在庫の型を指定する。
# Itemクラスインスタンスをキー、整数（在庫数量）をバリューとする辞書
Inventory = Dict[Item, int]


class Store:
    """店舗クラス
    残高および在庫状況を管理する。
    """

    def __init__(self):
        # 残高と在庫を初期化する
        self.balance = 10000  # type: int
        self.inventory = {}  # type: Inventory

    def buy(self, item: Item, amount: int) -> None:
        """仕入れ
        1. 商品を在庫に追加する
        2. 残高から商品代を引く
        """
        self.inventory.update({item: amount})
        self.balance -= item.purchace_price * amount

    def sell(self, item: Item, amount: int, selling_price: int) -> None:
        """販売
        1. 商品を在庫から指定数量分引く。
        2. 販売金額×販売数量分残高に追加する。
        """
        self.inventory[item] -= amount
        self.balance += selling_price * amount

    def clean_inventory(self, date: datetime.date) -> None:
        """在庫整理
        賞味期限切れ商品を在庫から削除する。
        数が0の商品を在庫から消す。
        """
        self.inventory = {
            item: amount
            for item, amount in self.inventory.items()
            if item.expires_at > date and amount != 0
        }


def generate_fish(date: datetime.date) -> Item:
    """水揚げ商品情報生成
    仕入れ値、商品名、賞味期限をランダムに作成する。
    """
    price = random.randint(100, 5000)
    name = f"{random.choice(harbors)}産 {random.choice(fish)}"
    expires_at = date + datetime.timedelta(days=random.randint(1, 3))
    return Item(name, price, expires_at)


def numeric_input(prompt: str) -> int:
    while True:
        _x = input(prompt)
        if _x.isnumeric():
            return int(_x)
        else:
            print("数字を入力してください\n")


def main() -> None:
    """
    1. 初期残高は10,000円に設定される。
    2. 毎日500円の販管費が引かれる。
    3. 商品は1日に何回でも仕入れられる。でも一度販売を実行したら
        翌日以降しか仕入れはできない。
    4. 残高がマイナスになったらゲームオーバー。
    5. 資産が10倍になったら勝ち。
    """
    s = Store()
    initial_balance = s.balance
    day = datetime.date.today()
    available_actions = [
        "1. 在庫をみる",
        "2. 商品を仕入れる",
        "3. 商品を売る",
        "4. 翌日にいく（販管費¥500円が差し引かれます）",
        "5. ゲーム終了",
    ]
    todays_actions = copy.deepcopy(available_actions)
    nl = "\n"

    while True:
        option_str = f"{nl}{day}{nl}残高：¥{s.balance} {'+' if s.balance >= initial_balance else ''}{round((s.balance / initial_balance - 1) * 100, 3)}%{nl}=====何をしますか？====={nl}{nl.join(todays_actions)}{nl}>"
        action = numeric_input(option_str)

        # 在庫をみる
        if action == 1:
            print(s.inventory)

        # 商品を仕入れる
        elif action == 2:
            if "2. 商品を仕入れる" not in todays_actions:
                continue

            # 3~6尾魚を出す
            fish_on_sale = [generate_fish(day) for _ in range(random.randint(3, 6))]
            for i, f in enumerate(fish_on_sale, 1):
                print(i, f)
            print(i + 1, "何も買わない")

            buy_ix = numeric_input(f"どの商品を買いますか？{nl}>") - 1

            if buy_ix < 0 or buy_ix >= i:
                continue

            buy_amount = numeric_input(f"何尾買いますか？{nl}>")

            s.buy(fish_on_sale[buy_ix], buy_amount)

        # 商品を売る
        elif action == 3:
            if "3. 商品を売る" not in todays_actions:
                continue

            # 今日の売値を決める
            for item, amount in s.inventory.items():
                # 売値入力
                selling_price = numeric_input(f"{item} の売値{nl}>")
                # 販売成功確率を計算
                prob = item.purchace_price / selling_price * random.uniform(0.8, 1.2)
                # 販売尾数を算出
                solds = sum(random.choices([1, 0], [prob, 1 - prob], k=amount))

                print(f"{solds}尾販売")
                s.sell(item, solds, selling_price)

            todays_actions.remove("2. 商品を仕入れる")
            todays_actions.remove("3. 商品を売る")

        elif action == 4:
            day += datetime.timedelta(days=1)
            s.balance -= 500
            todays_actions = copy.deepcopy(available_actions)

        elif action == 5:
            print("Bye")
            break

        if s.balance < 0:
            print(f"GAME OVER: 借金¥{s.balance}")
            break
        elif s.balance > initial_balance * 10:
            print(f"CONGRATULATIONS! 資産10倍おめでとうございます!")
            break

        s.clean_inventory(day)


if __name__ == "__main__":
    main()
