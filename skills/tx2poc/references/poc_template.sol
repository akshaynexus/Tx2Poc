// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.15;

import "../basetest.sol";

// @KeyInfo - Total Lost : {number unit}
// Attacker : {0x00000000000000000000000000000000cafebabe}
// Attack Contract : {0x00000000000000000000000000000000deadbeef}
// Vulnerable Contract : {0x00000000000000000000000000000000baddcafe}
// Attack Tx : {link: https://etherscan.io/tx/0x123456789}

// @Info
// Vulnerable Contract Code : {https://etherscan.io/address/0x00000000000000000000000000000000baddcafe#code}

// @Analysis
// Twitter Guy : {https://x.com/1nf0s3cpt/status/1583011233363824640}
//
// {Attack Summary}

address constant VULNERABLE_CONTRACT = 0x00000000000000000000000000000000baddcafe;
// Proxy/delegatecall cases: add ENTRY_STATE_CONTRACT and CODE_TARGET or IMPLEMENTATION constants.
// Call the entry/state address seen in the trace; use the implementation for source links and labels.

interface IVulnerableContract {
    function transfer(address to, uint256 amount) external returns (bool);
}

contract ContractTest is BaseTestWithBalanceLog {
    function setUp() public {
        attacker = 0x00000000000000000000000000000000cafebabe;
        fundingToken = address(0); // set to profit token for single-asset mode, or address(0) for native coin
        // multiAssetLog = true; // uncomment for multi-asset mode
        // _addFundingToken(0xTokenA); // add tokens individually
        // _addFundingTokens(new address[](2, [0xTokenA, 0xTokenB])); // or add multiple at once
        uint256 forkBlock = 15_460_093;
        vm.createSelectFork("mainnet", forkBlock);
        vm.label(attacker, "Attacker");
        vm.label(VULNERABLE_CONTRACT, "Vulnerable Contract");
    }

    // Single-asset mode: use balanceLog (logs fundingToken for attacker)
    // Multi-asset mode: use balanceLog (logs all fundingTokens[] when multiAssetLog = true)
    // Custom target: use balanceLog2(address) to log a specific address's balances
    function testExploit() public balanceLog {
        vm.startPrank(attacker);
        vm.stopPrank();
    }
}
