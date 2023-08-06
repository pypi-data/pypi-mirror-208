Feature: Payment Testing
  @smoke @regression
  Scenario: send valid payment
    Given we create "source" account for "Alice" with "default" XRP drops
      And we create "destination" account for "Bob" with "default" XRP drops
    When we send a payment of "2" XRP from Alice to Bob
    Then the balances after a valid payment are correct

  @smoke @regression
  Scenario: only submit a transaction
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we only submit a payment of "2" XRP from Alice to Bob
    Then the balances are correct in submit only mode

  @regression
  Scenario: send payment to self
    Given we create "source" account for "Alice" with "default" XRP drops
    When we send a payment of "2" XRP from Alice to self
    Then the self-payment should fail

  @regression
  Scenario: send payment with amount greater than balance
    Given we create "source" account for "Alice" with "default" XRP drops
      And we create "destination" account for "Bob" with "default" XRP drops
    When we send a payment with amount greater than balance from Alice to Bob
    Then the payment with amount greater than balance should fail

  @regression
  Scenario: send payment to invalid destination
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "invalid" account for "InvalidUser" with "default" XRP drops
    When we send a payment of "2" XRP from Alice to Invalid
    Then the payment with invalid destination should fail

  @regression
  Scenario: send payment with zero amount
    Given we create "source" account for "Alice" with "default" XRP drops
      And we create "destination" account for "Bob" with "default" XRP drops
    When we send a payment of "0" XRP from Alice to Bob
    Then the payment with zero amount should fail

  @regression
  Scenario: send payment with decimal amount
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we send a payment of "10.5" XRP from Alice to Bob
    Then the payment with decimal amount should fail

  @regression
  Scenario: send payment without source information
    Given we create "destination" account for "Bob" with "default" XRP drops
    When we send a payment of "2" XRP to Bob without providing source information
    Then the payment without source information should fail

  @regression
  Scenario: send payment without destination information
    Given we create "source" account for "Alice" with "default" XRP drops
    When we send a payment of "2" XRP from Alice without providing destination information
    Then the payment without destination information should fail

  @regression
  Scenario: send payment with 10 million XRP
    Given we create "source" account for "Alice" with "default" XRP drops
      And we create "destination" account for "Bob" with "default" XRP drops
    When we send a payment of "10000000000000" XRP from Alice to Bob
    Then the payment of 10 million XRP should fail

  @regression
  Scenario: send payment with non-xrp currency
    Given we create "source" account for "Alice" with "default" XRP drops
      And we create "destination" account for "Bob" with "default" XRP drops
    When we send a payment of "1000" USD from Alice to Bob
    Then the balances after a non-xrp payment are correct

  @regression
  Scenario: send payment with destination tag info
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we send a payment of "2" XRP with destination tag "123" info from Alice to Bob
    Then the balances after a payment with destination tag info are correct

  @regression
  Scenario: send payment with invoice id info
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we send a payment of "2" XRP with invoice id "6F1DFD1D0FE8A32E40E1F2C05CF1C15545BAB56B617F9C6C2D63A6B704BEF59B" from Alice to Bob
    Then the balances after a payment with invoice id info are correct

  @regression
  Scenario: send payment with invalid invoice id info
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we send a payment of "2" XRP with invoice id "123" from Alice to Bob
    Then the balances after a payment with invalid invoice id info are correct

  @regression
  Scenario: send payment from preauth account
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we send a payment of "2" XRP from Alice as a preauth account to Bob
    Then the balances after a payment from preauth account are correct

  @regression
  Scenario: send payment from non-preauth account
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we send a payment of "2" XRP from Alice as a non-preauth account to Bob
    Then the balances after a payment from non-preauth account are correct
