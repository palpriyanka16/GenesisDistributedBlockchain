$(document).ready(function() {
    $("#viewTxBtn").click(function() {
        if ($("#inputTransPath").val() == "") {
            $("#txDetails").css("display", "none");
        } else {
            $("#txDetails").css("display", "block");
            // ajax query to fetch transaction details and display response
        }
    });

    $("#AddTxnForm").submit(function(event) {
        event.preventDefault();
        var sender = $("#inputPubKey").val();
        var data = $("#inputTransData").val();
        var signature = $("#inputDigiSign").val();
        $.ajax({
            method: "POST",
            url: "http://localhost:8000/transaction",
            data: {
                sender: sender,
                data: data,
                signature: signature
            },
            success: function(result) {
                alert("Success");
            },
            error: function(error) {
                console.log(error);
            }
        });
    });

    $("#ViewTxn").submit(function(event) {
        event.preventDefault();
        var txHash = $("#inputTransPath").val();
        var blockHash = $("#inputBlockAddr").val();

        $.ajax({
            method: "GET",
            url: "http://localhost:8000/transaction",
            data: {
                txHash: txHash,
                blockHash: blockHash
            },
            success: function(result) {
                console.log(result);
                $("#txSign").html("<b>Sign: </b>" + result.data.signature);
                $("#txContent").html("<b>Data: </b>" + result.data.data);
                $("#txSender").html("<b>Sender: </b>" + result.data.sender);
            },
            error: function(error) {
                console.log(error);
            }
        });
    });

    $("#viewBCBtn").click(function() {
        //ajax query to fetch all blockchain details
        $.ajax({
            method: "GET",
            url: "http://localhost:8000/block/all",
            success: function(result) {
                console.log(result);
                constructBlockChainTable(result.data);
            },
            error: function(error) {
                console.log(error);
            }
        });

        function showModal(transactions) {
            var content = `<table class="table table-striped table-responsive">
                <tbody>
                    <tr>
                        <th>Data</th>
                        <th>Signature</th>
                        <th>Sender</th>
                        <th>Hash</th>
                    </tr>
            `;
            for (const [transactionHash, transaction] of Object.entries(transactions)) {
                content += `<tr>
                    <td>${transaction.data}</td>
                    <td>${transaction.signature}</td>
                    <td>${transaction.sender}</td>
                    <td>${transactionHash}</td>
                </tr>`;
            }
            content += `</tbody></table>`;
            $("#modalTxContent").html(content);
        }

        function constructBlockChainTable(blockChain) {
            var $table = `<table class="table table-striped">
                <tbody>
                    <tr>
                        <th>Block hash</th>
                        <th>Block height</th>
                        <th>Block nonce</th>
                    </tr>
            `;

            for (i = 0; i < blockChain.length; i++) {
                $table += `<tr>
                    <td style="cursor: pointer; color: blue;" data-toggle="modal" onclick="${showModal(blockChain[i].transactions)}" data-target="#blockTxModal">${blockChain[i].block_hash}</td>
                    <td>${blockChain[i].block_number}</td>
                    <td>${blockChain[i].nonce}</td>
                </tr>
                `;
            }
            $("#blockChainDiv").html($table);
        }
    });
});
