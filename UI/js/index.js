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
        console.log(sender);
        $.ajax({
            method: "POST",
            url: "http://localhost:8000/transaction",
            data: {
                sender: sender,
                data: data,
                signature: signature
            },
            success: function(result) {
                console.log(result);
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

        var $table = $('<table class="table table-striped">');
        var $tbody = $("<tbody>");
        var $tr1 = $("<tr>");
        var $th1 = $("<th>");
        var $th2 = $("<th>");
        var $th3 = $("<th>");
        $th1.text("Block hash");
        $th2.text("Block height");
        $th3.text("Block nonce");
        $tr1.append($th1);
        $tr1.append($th2);
        $tr1.append($th3);
        $tbody.append($tr1);

        $table.append($tbody);

        for (i = 1; i <= 4; i++) {
            var $tr = $("<tr>");
            var $td1 = $(
                '<td style="cursor: pointer; color: blue;" data-toggle="modal" onclick="showModal()" data-target="#blockTxModal">'
            );
            var $td2 = $("<td>");
            var $td3 = $("<td>");
            $td1.text(i);
            $td2.text(i);
            $td3.text(i);
            $tr.append($td1);
            $tr.append($td2);
            $tr.append($td3);
            $tbody.append($tr);
        }
        $("#blockChainDiv").html($table);
    });
});

function showModal() {
    document.getElementById("modalTxContent").innerHTML = "Transactions";
}
