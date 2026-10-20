Let's complete the Parking Lot LLD problem from beginning to end, but this time we'll focus on how to think, not just how to write code.

Your goal is to learn a process you can reuse for any LLD interview question:

1. How to identify classes.
2. How to identify attributes.
3. How to identify methods.
4. How to determine relationships between classes.
5. How to draw a class diagram.
6. How to translate the diagram into working code.

We'll use our Parking Lot problem throughout. We'll make each decision step by step, explaining why it belongs in the design.

# Step 1 — Define the requirements

Before identifying classes, write down what the system must do.

Our Parking Lot requirements are:

- Support multiple floors.
- Support motorcycles, cars, and trucks.
- Assign the smallest compatible spot, preferring the nearest spot within that size.
- Generate a ticket when a vehicle enters.
- Calculate parking fees based on exact parking duration and vehicle type.
- Release a spot only after successful payment.
- Show available parking spaces.

Why start here? Because classes should emerge from the requirements. If we begin with class names before understanding the behavior, we might create unnecessary classes or miss important ones.

# Step 2 — How to find classes

Here's the technique to use in an interview.

## Technique: nouns and responsibilities

Read the requirements and underline nouns representing things the system must remember or manage.

For example:

> A vehicle enters a parking lot. The system assigns a parking spot on a floor and generates a ticket. When the vehicle exits, the system calculates a fee and processes payment.

The candidate nouns are:

Vehicle

Has identity and type

ParkingLot

Coordinates operations

ParkingFloor

Organizes spots

ParkingSpot

Tracks occupancy

ParkingTicket

Records a parking session

Payment

Records a payment attempt/result

But don't blindly turn every noun into a class. For each candidate, ask three questions:

- Does the system need to remember its state?
- Does it have a meaningful identity or lifecycle?
- Does it have responsibilities that belong together?

For example, `ParkingTicket` deserves a class because it represents a particular parking session with an identity, entry time, and status. "Parking duration" can simply be a calculated value, so it doesn't necessarily need its own class.

We can also introduce service classes such as `FeeCalculator` and `SpotAssignmentStrategy` when we find behavior that benefits from being separated.

# Step 3 — How to find attributes

Once you have candidate classes, ask:

What information must the system remember about each object?

A useful rule is to identify the data required to support the methods in the requirements.

Let's derive the attributes one class at a time.

## 3.1 `Vehicle`

Ask: what must we know about a vehicle to park it?

- Its registration number, to identify it.
- Its type, to determine spot compatibility and pricing.

We have two design options:

- One `Vehicle` class with a `vehicle_type` attribute.
- An abstract `Vehicle` base class with `Car`, `Motorcycle`, and `Truck` subclasses.

For this exercise, we'll use subclasses to practice inheritance.

| Attribute       | Purpose                |
| --------------- | ---------------------- |
| `license_plate` | Identifies the vehicle |

The type is represented by the subclass, so we don't need a separate mutable `vehicle_type` field.

## 3.2 `ParkingSpot`

Ask: what information is necessary to find, occupy, and release a spot?

| Attribute | Purpose                                       |
| --------- | --------------------------------------------- |
| `spot_id` | Identifies the spot                           |
| `size`    | Determines compatible vehicles                |
| `x`, `y`  | Position for nearest-spot selection           |
| `vehicle` | The vehicle currently occupying it, or `None` |

Notice that we don't need a separate `is_occupied` Boolean. We can calculate occupancy using `vehicle is not None`.

Design lesson: Avoid storing the same information twice if one value can be derived from another. Duplicate state can become inconsistent.

## 3.3 `ParkingFloor`

Ask: what does one floor need to manage?

| Attribute      | Purpose                         |
| -------------- | ------------------------------- |
| `floor_number` | Identifies the floor            |
| `spots`        | Holds the floor's parking spots |

The floor doesn't need its own independent occupancy map because every spot already knows whether it is occupied.

## 3.4 `ParkingLot`

Ask: what does the entire lot need to coordinate parking?

| Attribute                  | Purpose                                       |
| -------------------------- | --------------------------------------------- |
| `floors`                   | All floors in the facility                    |
| `entrance_x`, `entrance_y` | Reference position for nearest-spot selection |

We don't need a second collection of occupied spots. We can inspect the spots on the floors.

## 3.5 `ParkingTicket`

Ask: what must we remember from entry until exit?

| Attribute    | Purpose                                  |
| ------------ | ---------------------------------------- |
| `ticket_id`  | Unique identifier for the session        |
| `vehicle`    | Vehicle associated with the session      |
| `spot`       | Assigned parking spot                    |
| `entry_time` | When parking began                       |
| `exit_time`  | When the session ended, initially `None` |
| `status`     | Whether the ticket is active or closed   |

Why not store the parking duration? Because it can be calculated from the entry and exit timestamps.

## 3.6 `FeeCalculator` and `Payment`

The fee calculator can use a mapping of vehicle type to hourly rate. It doesn't need to own the ticket or the vehicle.

For payment, we can introduce a `PaymentService` that processes the amount and reports success or failure. If we need a permanent payment record, we can model that separately as `Payment`.

At this point, our attributes are driven by requirements rather than guesses.

# Step 4 — How to find methods

Now ask a different question:

What actions must each class perform to fulfill its responsibilities?

Methods generally come from verbs in the requirements, plus operations needed to protect an object's state.

For example, "assign a spot" suggests a parking operation, while "release the spot" suggests a release operation.

Here's our initial method map.

| Class            | Methods                                                                              | Why?                                           |
| ---------------- | ------------------------------------------------------------------------------------ | ---------------------------------------------- |
| `Vehicle`        | `minimum_spot_size`                                                                  | Exposes the vehicle's minimum size requirement |
| `ParkingSpot`    | `is_available()`, `can_fit()`, `park()`, `release()`                                 | Checks compatibility and manages occupancy     |
| `ParkingFloor`   | `get_available_spots(vehicle)`                                                       | Finds candidates on one floor                  |
| `ParkingLot`     | `find_nearest_spot()`, `park_vehicle()`, `unpark_vehicle()`, `get_available_count()` | Coordinates lot-wide operations                |
| `ParkingTicket`  | `close(exit_time)`                                                                   | Ends a parking session                         |
| `FeeCalculator`  | `calculate_fee(ticket, exit_time)`                                                   | Calculates the exact-duration charge           |
| `PaymentService` | `process_payment(amount)`                                                            | Processes payment and returns a result         |

A few important distinctions:

- `ParkingSpot.park()` changes the state of one spot.
- `ParkingLot.park_vehicle()` coordinates the overall entry operation.
- `ParkingFloor.get_available_spots()` searches only one floor.
- `ParkingLot.find_nearest_spot()` compares candidates across all floors.

This is how you avoid putting every method into one giant class.

## How do we know which class owns a method?

Use this simple rule:

> Put a method on the class that owns the state it changes or the responsibility it performs.

For example, `release()` belongs naturally to `ParkingSpot`, because the spot owns its current occupant. `calculate_fee()` belongs to a pricing component, because pricing is independent of spot occupancy.

One method can call another. The point of LLD is to give each object a clear responsibility, not to prevent objects from collaborating.

# Step 5 — How to find relationships between classes

This is often the most confusing part of LLD. The easiest way is to ask how the objects interact in the real world.

There are four common relationships to recognize.

## 5.1 Composition — "contains and owns"

A parking lot contains floors, and each floor contains parking spots.

- `ParkingLot` contains `ParkingFloor` objects.
- `ParkingFloor` contains `ParkingSpot` objects.

We represent these as composition in our domain model because the lot manages the floors and each floor manages its spots.

In UML, composition uses a filled diamond at the owner end.

ParkingLot

1 owns many

ParkingFloor

Conceptually: ParkingLot ◆── ParkingFloor ◆── ParkingSpot. The filled diamond goes on the owning side.

In Python, these relationships can be implemented with ordinary lists. UML composition is a statement about ownership in our design, not a special Python feature.

## 5.2 Inheritance — "is a"

A car is a vehicle. A motorcycle is a vehicle. A truck is a vehicle.

Therefore:

- `Car` inherits from `Vehicle`.
- `Motorcycle` inherits from `Vehicle`.
- `Truck` inherits from `Vehicle`.

In UML, inheritance uses a solid line with a hollow triangle pointing to the parent class.

This is appropriate because all three share vehicle identity but can specify different minimum spot sizes.

## 5.3 Association — "knows or refers to"

A parking ticket refers to the vehicle and spot involved in that parking session.

It does not own the vehicle or spot.

For example, after a car leaves, the ticket can remain stored as a historical record while the spot is reused by another car.

In UML, association is represented by a solid line.

## 5.4 Dependency — "uses temporarily"

`FeeCalculator` uses ticket information to calculate a fee. `ParkingLot` uses a spot-assignment strategy to select a spot.

These classes can depend on other objects without owning their lifecycle. In UML, dependency is commonly shown using a dashed arrow.

### A quick way to remember the relationships

| Ask yourself                                        | Likely relationship |
| --------------------------------------------------- | ------------------- |
| Is one class a specialized type of another?         | Inheritance         |
| Does one class own and manage component objects?    | Composition         |
| Does one object keep a reference to another?        | Association         |
| Does one class use another to perform an operation? | Dependency          |

Don't force a relationship just because two classes interact. Choose the relationship that reflects the actual design.

# Step 6 — Draw the complete class diagram

Now we can combine everything we derived: classes, attributes, methods, and relationships.

\#chatgpt-mermaid-\_r_25i\_{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;fill:rgb(237, 237, 237);}@keyframes edge-animation-frame{from{stroke-dashoffset:0;}}@keyframes dash{to{stroke-dashoffset:0;}}#chatgpt-mermaid-\_r_25i\_ .edge-animation-slow{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 50s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_25i\_ .edge-animation-fast{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 20s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-\_r_25i\_ .error-icon{fill:rgb(48, 48, 48);}#chatgpt-mermaid-\_r_25i\_ .error-text{fill:rgb(237, 237, 237);stroke:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_25i\_ .edge-thickness-normal{stroke-width:1px;}#chatgpt-mermaid-\_r_25i\_ .edge-thickness-thick{stroke-width:3.5px;}#chatgpt-mermaid-\_r_25i\_ .edge-pattern-solid{stroke-dasharray:0;}#chatgpt-mermaid-\_r_25i\_ .edge-thickness-invisible{stroke-width:0;fill:none;}#chatgpt-mermaid-\_r_25i\_ .edge-pattern-dashed{stroke-dasharray:3;}#chatgpt-mermaid-\_r_25i\_ .edge-pattern-dotted{stroke-dasharray:2;}#chatgpt-mermaid-\_r_25i\_ .marker{fill:rgb(175, 175, 175);stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_25i\_ .marker.cross{stroke:rgb(175, 175, 175);}#chatgpt-mermaid-\_r_25i\_ svg{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;}#chatgpt-mermaid-\_r_25i\_ p{margin:0;}#chatgpt-mermaid-\_r_25i\_ g.classGroup text{fill:rgb(31, 78, 148);stroke:none;font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:10px;}#chatgpt-mermaid-\_r_25i\_ g.classGroup text .title{font-weight:bolder;}#chatgpt-mermaid-\_r_25i\_ .cluster-label text{fill:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_25i\_ .cluster-label span{color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_25i\_ .cluster-label span p{background-color:transparent;}#chatgpt-mermaid-\_r_25i\_ .cluster rect{fill:rgb(48, 48, 48);stroke:rgba(255, 255, 255, 0.15);stroke-width:1px;}#chatgpt-mermaid-\_r_25i\_ .cluster text{fill:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_25i\_ .cluster span{color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_25i\_ .nodeLabel,#chatgpt-mermaid-\_r_25i\_ .edgeLabel{color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_25i\_ .noteLabel .nodeLabel,#chatgpt-mermaid-\_r_25i\_ .noteLabel .edgeLabel{color:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_25i\_ .edgeLabel .label rect{fill:rgb(9, 23, 44);}#chatgpt-mermaid-\_r_25i\_ .label text{fill:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_25i\_ .labelBkg{background:rgb(9, 23, 44);}#chatgpt-mermaid-\_r_25i\_ .edgeLabel .label span{background:rgb(9, 23, 44);}#chatgpt-mermaid-\_r_25i\_ .classTitle{font-weight:bolder;}#chatgpt-mermaid-\_r_25i\_ .node rect,#chatgpt-mermaid-\_r_25i\_ .node circle,#chatgpt-mermaid-\_r_25i\_ .node ellipse,#chatgpt-mermaid-\_r_25i\_ .node polygon,#chatgpt-mermaid-\_r_25i\_ .node path{fill:rgb(9, 23, 44);stroke:rgb(31, 78, 148);stroke-width:1;}#chatgpt-mermaid-\_r_25i\_ .divider{stroke:rgb(31, 78, 148);stroke-width:1;}#chatgpt-mermaid-\_r_25i\_ g.clickable{cursor:pointer;}#chatgpt-mermaid-\_r_25i\_ g.classGroup rect{fill:rgb(9, 23, 44);stroke:rgb(31, 78, 148);}#chatgpt-mermaid-\_r_25i\_ g.classGroup line{stroke:rgb(31, 78, 148);stroke-width:1;}#chatgpt-mermaid-\_r_25i\_ .classLabel .box{stroke:none;stroke-width:0;fill:rgb(9, 23, 44);opacity:0.5;}#chatgpt-mermaid-\_r_25i\_ .classLabel .label{fill:rgb(31, 78, 148);font-size:10px;}#chatgpt-mermaid-\_r_25i\_ .relation{stroke:rgb(175, 175, 175);stroke-width:1;fill:none;}#chatgpt-mermaid-\_r_25i\_ .dashed-line{stroke-dasharray:3;}#chatgpt-mermaid-\_r_25i\_ .dotted-line{stroke-dasharray:1 2;}#chatgpt-mermaid-\_r_25i\_ [id$="-compositionStart"],#chatgpt-mermaid-\_r_25i\_ .composition{fill:rgb(175, 175, 175)!important;stroke:rgb(175, 175, 175)!important;stroke-width:1;}#chatgpt-mermaid-\_r_25i\_ [id$="-compositionEnd"],#chatgpt-mermaid-\_r_25i\_ .composition{fill:rgb(175, 175, 175)!important;stroke:rgb(175, 175, 175)!important;stroke-width:1;}#chatgpt-mermaid-\_r_25i\_ [id$="-dependencyStart"],#chatgpt-mermaid-\_r_25i\_ .dependency{fill:rgb(175, 175, 175)!important;stroke:rgb(175, 175, 175)!important;stroke-width:1;}#chatgpt-mermaid-\_r_25i\_ [id$="-dependencyEnd"],#chatgpt-mermaid-\_r_25i\_ .dependency{fill:rgb(175, 175, 175)!important;stroke:rgb(175, 175, 175)!important;stroke-width:1;}#chatgpt-mermaid-\_r_25i\_ [id$="-extensionStart"],#chatgpt-mermaid-\_r_25i\_ .extension{fill:transparent!important;stroke:rgb(175, 175, 175)!important;stroke-width:1;}#chatgpt-mermaid-\_r_25i\_ [id$="-extensionEnd"],#chatgpt-mermaid-\_r_25i\_ .extension{fill:transparent!important;stroke:rgb(175, 175, 175)!important;stroke-width:1;}#chatgpt-mermaid-\_r_25i\_ [id$="-aggregationStart"],#chatgpt-mermaid-\_r_25i\_ .aggregation{fill:transparent!important;stroke:rgb(175, 175, 175)!important;stroke-width:1;}#chatgpt-mermaid-\_r_25i\_ [id$="-aggregationEnd"],#chatgpt-mermaid-\_r_25i\_ .aggregation{fill:transparent!important;stroke:rgb(175, 175, 175)!important;stroke-width:1;}#chatgpt-mermaid-\_r_25i\_ [id$="-lollipopStart"],#chatgpt-mermaid-\_r_25i\_ .lollipop{fill:rgb(9, 23, 44)!important;stroke:rgb(175, 175, 175)!important;stroke-width:1;}#chatgpt-mermaid-\_r_25i\_ [id$="-lollipopEnd"],#chatgpt-mermaid-\_r_25i\_ .lollipop{fill:rgb(9, 23, 44)!important;stroke:rgb(175, 175, 175)!important;stroke-width:1;}#chatgpt-mermaid-\_r_25i\_ .edgeTerminals{font-size:11px;line-height:initial;}#chatgpt-mermaid-\_r_25i\_ .classTitleText{text-anchor:middle;font-size:18px;fill:rgb(237, 237, 237);}#chatgpt-mermaid-\_r_25i\_ .edgeLabel[data-look="neo"]{background-color:rgb(0, 0, 0);text-align:center;}#chatgpt-mermaid-\_r_25i\_ .edgeLabel[data-look="neo"] p{background-color:rgb(0, 0, 0);}#chatgpt-mermaid-\_r_25i\_ .edgeLabel[data-look="neo"] rect{opacity:0.5;background-color:rgb(0, 0, 0);fill:rgb(0, 0, 0);}#chatgpt-mermaid-\_r_25i\_ .label-icon{display:inline-block;height:1em;overflow:visible;vertical-align:-0.125em;}#chatgpt-mermaid-\_r_25i\_ .node .label-icon path{fill:currentColor;stroke:revert;stroke-width:revert;}#chatgpt-mermaid-\_r_25i\_ .node .neo-node{stroke:rgb(31, 78, 148);}#chatgpt-mermaid-\_r_25i\_ [data-look="neo"].node rect,#chatgpt-mermaid-\_r_25i\_ [data-look="neo"].cluster rect,#chatgpt-mermaid-\_r_25i\_ [data-look="neo"].node polygon{stroke:url(#chatgpt-mermaid-\_r_25i\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_25i\_ [data-look="neo"].swimlane.cluster rect{filter:none;}#chatgpt-mermaid-\_r_25i\_ [data-look="neo"].node path{stroke:url(#chatgpt-mermaid-\_r_25i\_-gradient);stroke-width:1px;}#chatgpt-mermaid-\_r_25i\_ [data-look="neo"].node .outer-path{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_25i\_ [data-look="neo"].node .neo-line path{stroke:rgb(31, 78, 148);filter:none;}#chatgpt-mermaid-\_r_25i\_ [data-look="neo"].node circle{stroke:url(#chatgpt-mermaid-\_r_25i\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_25i\_ [data-look="neo"].node circle .state-start{fill:#000000;}#chatgpt-mermaid-\_r_25i\_ [data-look="neo"].icon-shape .icon{fill:url(#chatgpt-mermaid-\_r_25i\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_25i\_ [data-look="neo"].icon-shape .icon-neo path{stroke:url(#chatgpt-mermaid-\_r_25i\_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-\_r_25i\_ :root{--mermaid-font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";}«abstract»Vehicle+license_plate: str+minimum_spot_size()MotorcycleCarTruckParkingSpot+spot_id: str+size: SpotSize+x: float+y: float+vehicle: Vehicle+is_available()+can_fit(vehicle)+park(vehicle)+release()ParkingFloor+floor_number: int+spots: list+get_available_spots(vehicle)ParkingLot+floors: list+entrance_x: float+entrance_y: float+find_nearest_spot(vehicle)+park_vehicle(vehicle)+unpark_vehicle(ticket_id)+get_available_count()ParkingTicket+ticket_id: str+vehicle: Vehicle+spot: ParkingSpot+entry_time: datetime+exit_time: datetime+status: TicketStatus+close(exit_time)FeeCalculator+hourly_rates: dict+calculate_fee(ticket, exit_time)PaymentService+process_payment(amount)occupied byrecordsrecordsusesuses110..10..\*0..\*1..\*0..\*0..111

Read this diagram in three passes:

1. Classes and their contents: the boxes show class names, attributes, and methods.
2. Inheritance: the hollow triangles show that the three vehicle types inherit from `Vehicle`.
3. Object relationships: diamonds indicate composition, solid lines indicate associations, and dashed arrows indicate dependencies.

The multiplicities are also useful:

- `1..*` means one or more.
- `0..*` means zero or more.
- `0..1` means zero or one.

For example, a floor may have zero or more spots, while a ticket refers to one vehicle and one spot.

This is our design blueprint. The exact associations can vary between implementations, but the responsibilities should remain clear.

# Step 7 — Connect the classes into one working flow

A class diagram shows the structure, but an interviewer also wants to know how the objects collaborate at runtime.

Let's trace both major operations.

## Vehicle entry

ParkingLot.park_vehicle(vehicle)

Ask each `ParkingFloor` for compatible, available spots

Rank candidates by size, distance, floor, and spot ID

`ParkingSpot.park(vehicle)`

Create and return a `ParkingTicket`

The ticket creation step is part of the full design, even though we left it out of the initial four-class implementation.

## Vehicle exit

ParkingLot.unpark_vehicle(ticket_id)

Validate that the ticket is active

`FeeCalculator.calculate_fee(ticket, exit_time)`

`PaymentService.process_payment(amount)`

Success

Close ticket and release spot

Failure

Keep ticket active and spot occupied

For exact-duration billing, if a car stays for 90 minutes and its hourly rate is ₹40, the fee is ₹60 before any taxes or additional rules.

One implementation detail: the ticket should only be closed after successful payment. In a production system, payment retries and uncertain payment outcomes need additional handling to prevent duplicate charges or inconsistent ticket state.

# Step 8 — Turn the design into code

Don't write every class at once. Implement in this order:

1. Domain types: `SpotSize`, `Vehicle`, `Motorcycle`, `Car`, `Truck`.
2. Spot management: `ParkingSpot` and its compatibility, occupancy, and release rules.
3. Floor management: `ParkingFloor` and candidate filtering.
4. Lot coordination: `ParkingLot` and the smallest-compatible, nearest-spot algorithm.
5. Parking session: `ParkingTicket` and unique ticket IDs.
6. Pricing and payment: `FeeCalculator`, `PaymentService`, and safe exit processing.
7. Testing: no spots available, incompatible vehicles, duplicate exits, payment failure, and equal-distance tie-breaking.

Only after the basic system works should we introduce an optional `SpotAssignmentStrategy` interface or additional pricing strategies. These make sense when we need interchangeable policies; they aren't required merely to complete the problem.

## The method to remember for your next LLD interview

## 1

Requirements → nouns

Find candidate objects and records that the system must represent.

## 2

Nouns → attributes

Ask what information each object must remember to support the requirements.

## 3

Verbs → methods

Assign each action to the class that owns the relevant data or responsibility.

## 4

Interactions → relationships

Decide which objects contain, inherit from, reference, or use other objects.

## 5

Changing rules → patterns

Introduce abstractions only when they help isolate behavior that varies.

## 6

Flow → code and tests

Implement and verify one use case at a time.

Your Parking Lot design is now mapped out from requirements through class relationships and the complete entry/exit flow. The next practical milestone is to implement the classes in that order and verify each stage, rather than trying to memorize the diagram or write the entire solution in one sitting.


Whenever you identify two classes, follow this decision process:
Take two classes, A and B

Is A a valid specialized type of B?
Yes
Inheritance

No
Continue


Does A own and manage B's lifecycle?
Yes
Composition

No
Continue


Does A keep a meaningful reference to B?
Yes
Association

No
Continue


Does A use B to perform an operation?
Dependency


<!-- https://chatgpt.com/c/6ace530c-f004-83e8-ac32-47c9e229f8c6 -->