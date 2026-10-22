import threading
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class Product:

    code:str
    name:str
    price_cents:int
    qty : int

    def __str__(self):
        return f"{self.code}: {self.name} - {self.price_cents / 100: .2f} ({self.qty} left)"
    
    def __post_init__(self):
        if self.price_cents < 0:
            raise ValueError("Price cannot be negative")
        if self.qty < 0:
            raise ValueError("Quantity cannot be negative")

class Inventory:

    def __init__(self):
        self.products: Dict[str, Product] = {}

    def add_product(self, p: Product):

        if p.code in self.products:
            existing = self.products[p.code]

            if existing.name != p.name or existing.price_cents != p.price_cents:
                raise ValueError("Product details do not match existing product")
            
            existing.qty += p.qty
        else:
            self.products[p.code] = p

    def get_product(self, code:str)-> Product:

        if code not in self.products:
            raise ValueError(f"Product with {code} is not available")

        return self.products[code]
    
    def list_products(self) -> List[Product]:

        product_list = []
        for k,v in self.products.items():
            product_list.append(v)

        return product_list
    
class CashBox:

    def __init__(self, denominations: list[int]):
        self.coins: Dict[int,int] = {d: 0 for d in denominations}
        self.sorted_denoms = sorted(denominations,reverse=True)
        if not denominations or any(d <= 0 for d in denominations):
            raise ValueError("Denominations must be positive")
        if len(set(denominations)) != len(denominations):
            raise ValueError("Duplicate denominations")

    def add_coins(self, denom:int, count:int):
        if denom not in self.coins:
            raise ValueError("Unsupported denomination")
        
        if count <= 0:
            raise ValueError("Count must be positive")
        
        self.coins[denom] += count

    def total_cents(self) -> int:

        return sum(d * c for d,c in self.coins.items())
    
    def make_change(self, amount_cents:int)-> Tuple[bool,Dict[int,int]]:

        if amount_cents < 0:
            return False,{}
        
        to_give , remaining = {}, amount_cents

        temp = self.coins.copy()

        for d in self.sorted_denoms:

            if remaining <= 0:
                break

            take = min(remaining // d , temp.get(d,0))
            if take:
                to_give[d] = take
                temp[d] -= take
                remaining -= d * take

        if remaining != 0:
            return False , {}
        
        for d,c in to_give.items():
            self.coins[d] -= c

        return True,to_give
    
    def accept_payment(self, payment: Dict[int,int]):

        for d,c in payment.items():
            if d not in self.coins:
                raise ValueError(f"Unsupported denomination: {d}")
            if c <= 0:
                raise ValueError("Coin count must be positive")

        for d,c in payment.items():    
            self.coins[d] += c
    
class VendingMachine:

    def __init__(self):
        self.denoms =[10000,5000,2000,1000,500,100,50,20,10,5,1]
        self.cashbox = CashBox(self.denoms)
        self.inventory = Inventory()
        self.lock = threading.Lock()
        self._send_demo()

    def _send_demo(self):

        self.inventory.add_product(Product("A1","Water Bottle",300,10))
        self.inventory.add_product(Product("A2","Soda Can",450,5))
        self.inventory.add_product(Product("B1","Chips",150,7))

        initial_coins = {100:30,50:20,20:30,10:50,5:100,1:200}

        for d,c in initial_coins.items():
            if d in self.cashbox.coins:
                self.cashbox.add_coins(d,c)

    def list_products(self):

        for p in self.inventory.list_products():
            print(p)

    def restock(self, code:str, qty: int):

        if qty <= 0:
            raise ValueError("Restock quantity must be positive")

        with self.lock:
            try:
                p = self.inventory.get_product(code)
            except ValueError:
                print("Product not found.")
                return
            
            p.qty += qty
            print(f"Restocked {code}. New Qty: {p.qty}")

    def refill_coins(self,denom:int,count:int):
        with self.lock:
            self.cashbox.add_coins(denom,count)
            print(f"Refilled {count} coins of {denom} cents")


    def purchase(self, code:str , payment:Dict[int,int]):

        with self.lock:
            try:
                product = self.inventory.get_product(code)
            except ValueError:
                return False, "Product not found"
            
            if product.qty <= 0:
                return False, "Out of Stock"
            
            if not payment:
                return False, "Payment required"
            
            for denom , count in payment.items():
                if denom not in self.cashbox.coins:
                    return False, f"Unsupported denomination: {denom}"
                if count <= 0:
                    return False, "Coin count must be positive"

            total = sum(d*c for d,c in payment.items())
            price = product.price_cents

            if total < price:
                return False, "Insufficient money"
            
            change_needed = total - price

            temp_cashbox = CashBox(self.denoms)
            temp_cashbox.coins = self.cashbox.coins.copy()
            temp_cashbox.accept_payment(payment)

            success, change_map = temp_cashbox.make_change(change_needed)
            if not success:
                return False, "Cannot provide change"
            
            self.cashbox.coins = temp_cashbox.coins
            product.qty -= 1

            return True,{
                "Product":product.name,
                "change_map": change_map
            }


def demo():
    vm = VendingMachine()

    print("Welcome to Demo Vending Machine. ")

    while True:
        print("\n-- Menu --")
        print("1) List Products")
        print("2) Purchase")
        print("3) Restock (admin)")
        print("4) Refill coins (admin)")
        print("5) Exit")

        choice = input("Choose: ").strip()
        if choice == "1":
            vm.list_products()
        if choice == "2":
            vm.list_products()
            code = input("Enter product code: ").strip()
            print("Enter payment denominations as 'denom_in_cents:count' seperated by commas. ")
            print("Example: 100:2,50:1 -> 2.50")
            entry = input("Payment: ").strip()
            try:
                payment = {}
                for part in filter(None,map(str.strip,entry.split(","))):
                    d_s,c_s = part.split(":")
                    d = int(d_s); c = int(c_s)
                    payment[d] = payment.get(d,0) + c
                ok,result = vm.purchase(code,payment)
                if not ok:
                    print("Falied:",result)
                else:
                    print(f"Dispensed: {result['Product']}")
                    if result["change_map"]:
                        print("Change:")
                        for d,c in result["change_map"].items():
                            print(f"{c} coins of {d} cents")
            except (ValueError, TypeError):
                print("Invalid input or payment")
        if choice == "3":
            code = input("Enter product code: ").strip()
            qty = int(input("Enter quantity: ").strip())
            vm.restock(code,qty)
        if choice == "4":
            denom = int(input("Enter denom: ").strip())
            count = int(input("Enter count: ").strip())
            vm.refill_coins(denom,count)
        if choice == "5":
            break

    print("Goodbye")

if __name__ == "__main__":

    demo()

