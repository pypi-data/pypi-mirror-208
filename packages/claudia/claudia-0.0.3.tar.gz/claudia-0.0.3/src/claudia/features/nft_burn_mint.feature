Feature: NFT Burn Mint Testing
  @regression
  Scenario: mint NFT using same token taxon
    Given we create "source" account for "Alice" with "default" XRP drops
    When we mint NFT using same token taxon
    Then nft minting is successful

  @regression
  Scenario: mint NFT with low reserves
    Given we create "source" account for "Alice" with "10000000" XRP drops
    When we mint NFT with low reserves
    Then nft minting with low reserves is not successful

  @regression
  Scenario: mint NFT with optional URI as a string
    Given we create "source" account for "Alice" with "default" XRP drops
    When we mint NFT with optional URI as a string
    Then nft minting with optional URI as a string is not successful

  @regression
  Scenario: mint NFT with optional URI as a hex string
    Given we create "source" account for "Alice" with "default" XRP drops
    When we mint NFT with optional URI as a hex string
    Then nft minting with optional URI as a hex string is not successful

  @regression
  Scenario: mint NFT with invalid URI
    Given we create "source" account for "Alice" with "default" XRP drops
    When we mint NFT with invalid URI
    Then nft minting with invalid URI is not successful

  @regression
  Scenario: mint NFT with optional URI with more than 265 characters
    Given we create "source" account for "Alice" with "default" XRP drops
    When we mint NFT with optional URI with more than 265 characters
    Then nft minting with optional URI with more than 265 characters is not successful

  @regression
  Scenario: mint NFT with optional negative transfer fee
    Given we create "source" account for "Alice" with "default" XRP drops
    When we mint NFT with optional "-1" transfer fee
    Then nft minting with optional negative transfer fee is not successful

  @regression
  Scenario: mint NFT with optional zero transfer fee
    Given we create "source" account for "Alice" with "default" XRP drops
    When we mint NFT with optional "0" transfer fee
    Then nft minting with optional zero transfer fee is successful

  @regression
  Scenario: mint NFT with optional transfer fee in decimal
    Given we create "source" account for "Alice" with "default" XRP drops
    When we mint NFT with optional "10.5" transfer fee
    Then nft minting with optional transfer fee in decimal is not successful

  @regression
  Scenario: mint NFT with optional transfer fee more than 50000
    Given we create "source" account for "Alice" with "default" XRP drops
    When we mint NFT with optional "50001" transfer fee
    Then nft minting with optional transfer fee more than 50000 is not successful

  @regression
  Scenario: mint NFT without tfTransferable flag
    Given we create "source" account for "Alice" with "default" XRP drops
    When we mint NFT without tfTransferable flag
    Then nft minting without tfTransferable flag is not successful

  @regression
  Scenario: mint NFT with optional memos
    Given we create "source" account for "Alice" with "default" XRP drops
    When we mint NFT with optional memos
    Then nft minting with optional memos is successful

  @regression
  Scenario: mint NFT with bad seed
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we mint NFT with bad seed
    Then nft minting with bad seed is not successful

  @regression
  Scenario: mint NFT without nftoken_taxon
    Given we create "source" account for "Alice" with "default" XRP drops
    When we mint NFT without nftoken_taxon
    Then nft minting without nftoken_taxon is not successful

  @regression
  Scenario: mint NFT with negative nftoken_taxon
    Given we create "source" account for "Alice" with "default" XRP drops
    When we mint NFT with negative nftoken_taxon
    Then nft minting with negative nftoken_taxon is not successful

  @regression
  Scenario: mint NFT with too high nftoken_taxon
    Given we create "source" account for "Alice" with "default" XRP drops
    When we mint NFT with too high nftoken_taxon
    Then nft minting with too high nftoken_taxon is not successful

  @regression
  Scenario: mint NFT without source account field
    Given we create "source" account for "Alice" with "default" XRP drops
    When we mint NFT without source account field
    Then nft minting without source account field is not successful

  @regression
  Scenario: mint NFT with empty source account field
    Given we create "source" account for "Alice" with "default" XRP drops
    When we mint NFT with empty source account field
    Then nft minting with empty source account field is not successful

  @regression
  Scenario: mint NFT with same account as issuer
    Given we create "source" account for "Alice" with "default" XRP drops
    When we mint NFT with same account as issuer
    Then nft minting with same account as issuer is not successful

  @regression
  Scenario: mint NFT with invalid issuer
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "invalid" account for "InvalidUser" with "default" XRP drops
    When we mint NFT with invalid issuer
    Then nft minting with invalid issuer is not successful

  @regression
  Scenario: mint NFT with issuer having unauthorized user
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we mint NFT with issuer having unauthorized user
    Then nft minting with issuer having unauthorized user is not successful

  @regression
  Scenario: mint NFT with issuer having authorized user
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we mint NFT with issuer having authorized user
    Then nft minting with issuer having authorized user is successful

  @regression
  Scenario: mint NFT on ticket with issuer having authorized user
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we mint NFT on ticket with authorized user
    Then nft minting on ticket with authorized user is successful

  @regression
  Scenario: mint NFT on ticket with issuer without user authorization
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we mint NFT on ticket with issuer without user authorization
    Then nft minting on ticket with issuer without user authorization is not successful

  @regression
  Scenario: mint NFT with issuer and remove authorization
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we mint NFT with issuer and remove authorization
    Then nft minting with issuer and removing authorization is successful

  @regression
  Scenario: change authorized user and mint NFT
    Given we create "generic_alice" account for "Alice" with "default" XRP drops
    And we create "generic_bob" account for "Bob" with "default" XRP drops
    And we create "generic_carol" account for "Carol" with "default" XRP drops
    When we change authorized user and mint NFT
    Then NFT minting after changing authorized user is successful

  @regression
  Scenario: mint NFT using authorization chain of authorized users
    Given we create "generic_alice" account for "Alice" with "default" XRP drops
    And we create "generic_bob" account for "Bob" with "default" XRP drops
    And we create "generic_carol" account for "Carol" with "default" XRP drops
    When we mint NFT using authorization chain of authorized users
    Then NFT minting using authorization chain of authorized users is not successful

  @regression
  Scenario: mint NFT using ticket
    Given we create "source" account for "Alice" with "default" XRP drops
    When we mint NFT using ticket
    Then NFT minting using ticket is successful

  @regression
  Scenario: mint NFT and delete account owner
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we mint NFT and try to delete account owner
    Then deleting account owner after NFT minting is not successful

  @regression
  Scenario: mint NFT on ticket and delete account owner
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we mint NFT on ticket and try to delete account owner
    Then deleting account owner after NFT minting on ticket is not successful

  @regression
  Scenario: mint NFT with issuer and then remove authorization and delete account owner
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we mint NFT with issuer and then remove authorization and delete account owner
    Then removing authorization and deleting account owner after NFT minting is not successful

  @regression
  Scenario: mint NFT with issuer and then remove authorization and delete issuer
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we mint NFT with issuer and then remove authorization and delete issuer
    Then removing authorization and deleting issuer after NFT minting is not successful

  @smoke @regression
  Scenario: burn NFT as owner
    Given we create "source" account for "Alice" with "default" XRP drops
    When we burn NFT as owner
    Then burning NFT as owner is successful

  @regression
  Scenario: burn NFT with low reserves
    Given we create "source" account for "Alice" with "14000000" XRP drops
    And we create "destination" account for "Bob" with "10000000" XRP drops
    When we burn NFT with low reserves
    Then burning NFT with low reserves is not successful

  @regression
  Scenario: burn NFT with NFT ID mismatch
    Given we create "source" account for "Alice" with "default" XRP drops
    When we burn NFT with NFT ID mismatch
    Then burning NFT with NFT ID mismatch is not successful

  @regression
  Scenario: burn NFT as different user
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we burn NFT as different user
    Then burning NFT as different user is not successful

  @regression
  Scenario: mint NFT with issuer burn as owner
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we mint NFT with issuer burn as owner
    Then burning NFT with issuer burn as owner is successful

  @regression
  Scenario: mint NFT with issuer burn as issuer without tfBurnable
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we mint NFT with issuer burn as issuer without tfBurnable
    Then burning NFT with issuer burn as issuer without tfBurnable is not successful

  @regression
  Scenario: mint NFT with issuer burn as issuer with tfBurnable
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we mint NFT with issuer burn as issuer with tfBurnable
    Then burning NFT with issuer burn as issuer with tfBurnable is successful

  @regression
  Scenario: mint NFT with issuer burn as issuer without owner field
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we mint NFT with issuer burn as issuer without owner field
    Then burning NFT with issuer burn as issuer without owner field not successful

  @regression
  Scenario: burn NFT and remint
    Given we create "source" account for "Alice" with "default" XRP drops
    When we burn NFT and remint
    Then burning NFT and reminting is successful

  @time_intensive  @regression
  Scenario: burn NFT and delete owner
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we burn NFT and delete owner
    Then burning NFT and deleting owner is successful

  @time_intensive  @regression
  Scenario: mint NFT with issuer burn as owner and delete owner
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we mint NFT with issuer burn as owner and delete owner
    Then minting NFT with issuer burn as owner and deleting owner is successful

  @time_intensive  @regression
  Scenario: burn NFT as owner and delete issuer
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we burn NFT as owner and delete issuer
    Then burning NFT as owner and deleting issuer is successful

  @time_intensive  @regression
  Scenario: burn NFT as owner and delete owner
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we burn NFT as issuer and delete owner
    Then burning NFT as issuer and deleting owner is successful

  @time_intensive  @regression
  Scenario: burn NFT as issuer and delete issuer
    Given we create "source" account for "Alice" with "default" XRP drops
    And we create "destination" account for "Bob" with "default" XRP drops
    When we burn NFT as issuer and delete issuer
    Then burning NFT as issuer and deleting issuer is successful

  @time_intensive  @regression
  Scenario: mint more than 32 NFT objects
    Given we create "source" account for "Alice" with "default" XRP drops
    When we mint more than 32 NFT objects
    Then minting more than 32 NFT objects is successful
