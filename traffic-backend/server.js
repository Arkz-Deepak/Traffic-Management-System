const express = require('express');
const cors = require('cors');
const WebSocket = require('ws'); // Using raw WebSockets instead of roslib

const app = express();
app.use(cors());
app.use(express.json());

// 1. Connect directly to ROS Bridge
const ws = new WebSocket('ws://localhost:9090');

ws.on('open', () => {
    console.log('Connected to AURA ROS 2 DDS Network (Raw WS Connection).');
    
    // We have to 'advertise' the topic once so the ROS network knows we intend to publish
    ws.send(JSON.stringify({
        op: 'advertise',
        topic: '/frontend/emergency_path',
        type: 'std_msgs/msg/String'
    }));
});

ws.on('error', (error) => {
    console.error('WebSocket Error: ', error);
});

// 2. The API Endpoint for your React Dashboard
app.post('/api/dispatch-ambulance', (req, res) => {
    const routeArray = req.body.route; 
    const routeString = routeArray.join(','); 
    
    // 3. Construct the exact JSON payload ROS Bridge expects
    const rosPayload = {
        op: 'publish',
        topic: '/frontend/emergency_path',
        msg: {
            data: routeString
        }
    };

    // Fire it directly down the TCP pipe
    if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(rosPayload));
        console.log(`Dispatched Green Wave route to ROS 2: ${routeString}`);
        res.status(200).send({ message: "Green Wave Initiated" });
    } else {
        console.log("Failed: WebSocket not connected to ROS.");
        res.status(500).send({ error: "ROS Bridge disconnected" });
    }
});

app.listen(3000, () => {
    console.log("AURA Backend listening on port 3000");
});