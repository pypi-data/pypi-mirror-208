Feature: Trustline Testing
  @regression
  Scenario: send one currency payment
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we send a trustline payment using one currency from Alice to Bob
    Then trustline payment using one currency is successful

  @regression
  Scenario: send issued currency payment
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    And we create "issuer" account for "Issuer" with "default" XRP drops
    When we send issued currency payment from Alice to Bob
    Then issued currency payment is successful

  @regression
  Scenario: send issued currency payment without trustline
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    And we create "issuer" account for "Issuer" with "default" XRP drops
    When we send issued currency payment without trustline from Alice to Bob
    Then issued currency payment without trustline is not successful

########## May not be possible with both Python and JS client.
########## Both Py and JS Client lib does not use ignore_defaults param.
####  @regression
####  Scenario: send issued currency payment ignoring defaults
####    Given we create "source" account for "Alice" with "default" XRP drops
####    And we create "destination" account for "Bob" with "default" XRP drops
####    When we send issued currency payment ignoring defaults from Alice to Bob
####    Then issued currency payment ignoring defaults is not successful

  @regression
  Scenario: send issued currency payment in decimals
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we send issued currency payment in decimals from Alice to Bob
    Then issued currency payment in decimal is successful

#### May not be possible with JS client! Client lib allows floats.
#### JS does not allow non-string values. For now, just returning early in JS implementation.
  @regression
  Scenario: send issued currency payment in non-string decimals
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we send issued currency payment in non-string decimals from Alice to Bob
    Then issued currency payment in non-string decimal is successful

  @regression
  Scenario: send issued currency payment with invalid issuer
    Given we create "invalid" account for "Invalid" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we send issued currency payment from Invalid issuer to Bob
    Then issued currency payment from Invalid issuer is not successful

  @regression
  Scenario: send issued currency payment to Invalid recipient
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "invalid" account for "Invalid" with "default" XRP drops
    When we send issued currency payment from Alice to Invalid recipient
    Then issued currency payment to invalid recipient is not successful

  @regression
  Scenario: establish trustline with non-standard currency code
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we establish trustline with "default" amount in "0158415500000000C1F76FF6ECB0BAC600000000" currency code
    Then trustline creation with non-standard currency code is successful

  @regression
  Scenario: establish trustline with invalid currency code '---'
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we establish trustline with "default" amount in "---" currency code
    Then trustline creation with invalid currency code --- fails

  @regression
  Scenario: establish trustline with invalid currency code 'USDX'
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we establish trustline with "default" amount in "USDX" currency code
    Then trustline creation with invalid currency code USDX fails

  @regression
  Scenario: establish trustline to self
    Given we create "source" account for "Alice" with "default" XRP drops
    When we establish trustline from Alice to self
    Then trustline creation to self is not successful

  @regression
  Scenario: establish trustline with invalid currency code 'XRP'
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we establish trustline with "default" amount in "XRP" currency code
    Then trustline creation with invalid currency code XRP fails

  @regression
  Scenario: establish trustline with negative limit amount
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we establish trustline with "-100" amount in "USD" currency code
    Then trustline creation with negative limit amount is not successful

  @regression
  Scenario: establish trustline with zero limit amount
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we establish trustline with "0" amount in "USD" currency code
    Then trustline creation with zero limit amount is not successful

  @regression
  Scenario: send issued currency payment with amount more than limit amount
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we send issued currency payment with amount more than limit amount from Alice to Bob
    Then issued currency payment with amount more than limit amount recipient is not successful

  @regression
  Scenario: send cross currency payment using BTC and USD
    Given we create "generic_alice" account for "Alice" with "default" XRP drops
    And we create "generic_bob" account for "Bob" with "default" XRP drops
    And we create "generic_carol" account for "Carol" with "default" XRP drops
    And we create "issuer" account for "Issuer" with "default" XRP drops
    When we send cross currency payment using BTC and USD
    Then cross currency payment using BTC and USD is successful

  @regression
  Scenario: send cross currency payment using BTC and USD without specifying paths
    Given we create "generic_alice" account for "Alice" with "default" XRP drops
    And we create "generic_bob" account for "Bob" with "default" XRP drops
    And we create "generic_carol" account for "Carol" with "default" XRP drops
    And we create "issuer" account for "Issuer" with "default" XRP drops
    When we send cross currency payment using BTC and USD without specifying paths
    Then cross currency payment using BTC and USD without specifying paths is successful

  @regression
  Scenario: send cross currency payment using BTC and USD with offer and payment
    Given we create "generic_alice" account for "Alice" with "default" XRP drops
    And we create "generic_bob" account for "Bob" with "default" XRP drops
    And we create "generic_carol" account for "Carol" with "default" XRP drops
    And we create "issuer" account for "Issuer" with "default" XRP drops
    When we send cross currency payment using BTC and USD with offer and payment
    Then cross currency payment using BTC and USD with offer and payment is successful

  @regression
  Scenario: send cross currency payment using XRP and USD
    Given we create "generic_alice" account for "Alice" with "default" XRP drops
    And we create "generic_bob" account for "Bob" with "default" XRP drops
    And we create "generic_carol" account for "Carol" with "default" XRP drops
    And we create "issuer" account for "Issuer" with "default" XRP drops
    When we send cross currency payment using XRP and USD
    Then cross currency payment using XRP and USD is successful

  @regression
  Scenario: send cross currency payment to self using XRP and USD
    Given we create "generic_alice" account for "Alice" with "default" XRP drops
    And we create "generic_bob" account for "Bob" with "default" XRP drops
    And we create "issuer" account for "Issuer" with "default" XRP drops
    When we send cross currency payment to self using XRP and USD
    Then cross currency payment to self using XRP and USD is not successful

  @regression
  Scenario: send cross currency payment using USD and XRP
    Given we create "generic_alice" account for "Alice" with "default" XRP drops
    And we create "generic_bob" account for "Bob" with "default" XRP drops
    And we create "generic_carol" account for "Carol" with "default" XRP drops
    And we create "issuer" account for "Issuer" with "default" XRP drops
    When we send cross currency payment using USD and XRP
    Then cross currency payment using USD and XRP is successful

  @regression
  Scenario: send cross currency payment using USD and XRP without specifying send_max
    Given we create "generic_alice" account for "Alice" with "default" XRP drops
    And we create "generic_bob" account for "Bob" with "default" XRP drops
    And we create "generic_carol" account for "Carol" with "default" XRP drops
    And we create "issuer" account for "Issuer" with "default" XRP drops
    When we send cross currency payment using USD and XRP without specifying send_max
    Then cross currency payment using USD and XRP without specifying send_max fails

  @regression
  Scenario: send cross currency payment using BTC, USD and XRP
    Given we create "generic_alice" account for "Alice" with "default" XRP drops
    And we create "generic_bob" account for "Bob" with "default" XRP drops
    And we create "generic_carol" account for "Carol" with "default" XRP drops
    And we create "issuer" account for "Issuer" with "default" XRP drops
    When we send cross currency payment using BTC, USD and XRP
    Then cross currency payment using BTC, USD and XRP is successful

  @regression
  Scenario: send cross currency payment using BTC, USD and XRP without specifying paths
    Given we create "generic_alice" account for "Alice" with "default" XRP drops
    And we create "generic_bob" account for "Bob" with "default" XRP drops
    And we create "generic_carol" account for "Carol" with "default" XRP drops
    And we create "issuer" account for "Issuer" with "default" XRP drops
    When we send cross currency payment using BTC, USD and XRP without specifying paths
    Then cross currency payment using BTC, USD and XRP without specifying paths is not successful
