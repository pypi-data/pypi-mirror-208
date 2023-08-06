#!python3
""" Infinite State Machine to implement a conversational Agent 

Import and export from the v3.dialog.yaml format.

### References

* [python-statemaching](https://pypi.org/project/python-statemachine/)

Example schema to start with (before migrating to `v2.dialog.yaml`

#### *`schema`*
```yaml
- 
  - activity
  - state name and args 
  - bot message
    - human intent numerical answer: destination check answer state
    - human intent command: destination action/eval state
    - human intent question: destination FAQ answer state
    - human intent conversation: destination conversation rapport state
    - else: fallback destination state
```

#### *`example counting activity`*      
```yaml
- 
  - count 1
  - welcome 1 1 3
  - Welcome! Lets count! Next number after 1, 2, 3 ?
    - 4: question 1 6 3
    - else: hint 1 1 3

- 
  - count 1
  - hint 1 1 3
  - what is 1 more than 3?
    - 4: question 1 2 3
    - else: hint 1 1 3
    
- 
  - count 1
  - question 1 1 3
  - Next number after 1, 2, 3 ?
    - 4: question 1 6 3
    - else: hint 1 1 3

- 
  - count 1
  - question 1 2 3
  - Next number after 2, 3, 4?
    - 5: question 1 6 3
    - else: hint 1 2 3

- 
  - count 1
  - hint 1 1 3
  - what is 1 more than 3?
    - 4: question 1 2 3
    - else: hint 1 1 3
```
"""
from statemachine import StateMachine, State


class OrderControl(StateMachine):
    """State machine for processing purchases of a single commodity item

    >>> control = OrderControl()
    >>> control.add_to_order(3)
    3
    >>> control.add_to_order(7)
    10
    >>> control.receive_payment(4)
    [4]
    >>> control.current_state.id
    'waiting_for_payment'
    """

    waiting_for_payment = State("Waiting for payment", initial=True)
    processing = State("Processing")
    shipping = State("Shipping")
    completed = State("Completed", final=True)

    add_to_order = waiting_for_payment.to(waiting_for_payment)
    receive_payment = waiting_for_payment.to(
        processing, cond="payments_enough"
    ) | waiting_for_payment.to(waiting_for_payment, unless="payments_enough")
    process_order = processing.to(shipping, cond="payment_received")
    ship_order = shipping.to(completed)

    def __init__(self):
        self.order_total = 0
        self.payments = []
        self.payment_received = False
        super(OrderControl, self).__init__()

    def payments_enough(self, amount):
        return sum(self.payments) + amount >= self.order_total

    def before_add_to_order(self, amount):
        self.order_total += amount
        return self.order_total

    def before_receive_payment(self, amount):
        self.payments.append(amount)
        return self.payments

    def after_receive_payment(self):
        self.payment_received = True

    def on_enter_waiting_for_payment(self):
        self.payment_received = False


if __name__ == "__main__":
    print("control = OrderControl()")
    control = OrderControl()

    print("control.add_to_order(3)")
    print(control.add_to_order(3))

    print("control.add_to_order(7)")
    print(control.add_to_order(7))

    print("control.receive_payment(4)")
    print(control.receive_payment(4))

    print("control.current_state.id")
    print(control.current_state.id)

    from statemachine.contrib.diagram import DotGraphMachine

    graph = DotGraphMachine(OrderControl)  # also accepts instances
    dot = graph()
    dot.to_string()
    dot.write_png("docs/order_control_machine_initial.png")
