<?php
include './process.php';
header('Content-Type: application/json'); // <- Required for JSON responses

$term = $_GET['term'] ?? '';

$suggestions = [];
if (!empty($term)) {
    $stmt = $conn->prepare("SELECT title FROM article WHERE title LIKE CONCAT('%', ?, '%') LIMIT 10");
    $stmt->bind_param("s", $term);
    $stmt->execute();
    $result = $stmt->get_result();

    while ($row = $result->fetch_assoc()) {
        $suggestions[] = $row['title'];
    }

    $stmt->close();
}

echo json_encode($suggestions);
$conn->close();
?>
