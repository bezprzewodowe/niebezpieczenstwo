<!DOCTYPE html>
<html lang="pl">
    <head>
        <meta http-equiv="content-type" content="text/html;charset=utf-8">
        <title>probe</title>
        <style type="text/css">
            * {
                font-family: monospace;
                font-size: 12px;
            }
            table {
                border-collapse: collapse;
            }
            table, th, td {
                border: 1px solid black;
            }
            td {
                padding: 5px;
            }
        </style> 
    </head>
    <body>
        <?php
// (C) 2016 Adam Ziaja <adam@adamziaja.com> http://adamziaja.com

$servername = "localhost";
$username   = "tapt";
$password   = "toor";
$dbname     = "tapt";

$conn = new mysqli($servername, $username, $password, $dbname);
$conn->set_charset("utf8");

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

$mac = $_GET['mac'];

if (preg_match('/^([a-fA-F0-9]{2}:){5}[a-fA-F0-9]{2}$/', $mac)) {
    $sql = "SELECT probe.mac, probe.ssid, geo.gps, geo.address FROM probe INNER JOIN geo ON probe.ssid=geo.ssid WHERE probe.mac = '$mac'";
} else {
    $sql = "SELECT probe.mac, probe.ssid, geo.gps, geo.address FROM probe INNER JOIN geo ON probe.ssid=geo.ssid ORDER BY probe.mac, probe.ssid";
}
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    echo "<table>";
    echo "<tr><th>mac</th><th>ssid</th><th>gps</th><th>address</th></th>";
    while ($row = $result->fetch_assoc()) {
        $mac     = $row["mac"];
        $ssid    = $row["ssid"];
        $gps     = $row["gps"];
        $address = $row["address"];
        echo "<tr><td><a href='?mac=$mac'>$mac</a></td><td>$ssid</td><td><a href='https://www.google.pl/maps?q=$gps' target='_blank'>$gps</a></td><td>$address</td></tr>" . PHP_EOL;
    }
    echo "</table>";
    echo "<p><a href='?'>&laquo; wróć</a></p>";
} else {
    echo "błąd?";
}

$conn->close();
?>
    </body>
</html>
