$(document).ready(function() {

    var socket = io();

    socket.on('connect', function() {
        console.log('Connected to the server');
    });



    socket.on('code_message', function(message) {
        console.log('code_message')
        document.getElementById('python-code').innerHTML = `<code class="language-python">${message.content}</code>`;
        Prism.highlightAll();
        
    });
    socket.on('sketch_message', function(message) {
        console.log('sketch_message')
        const imageContainer = document.getElementById('sketch-container');
        imageContainer.innerHTML = '';
        const img = document.createElement('img');
        img.src = message.url;
        img.alt = "Requested Image";
        img.style.maxWidth = "100%";  // 可选：设置图片样式
        // 将图片添加到容器中
        imageContainer.appendChild(img);

        
    });

    socket.on('multiview_message', function(message) {
        console.log('multiview_message!!')
        const imageContainer = document.getElementById('multiview-container');
        imageContainer.innerHTML = '';
        const img = document.createElement('img');
        img.src = message.url;
        img.alt = "Requested Image";
        img.style.maxWidth = "100%";  // 可选：设置图片样式
        // 将图片添加到容器中
        imageContainer.appendChild(img);

        
    });
    socket.on('plan_message', function(message) {
        console.log('plan_message')
        const formatter = new JSONFormatter(message, 4);
        const container = document.getElementById("plan");
        container.innerHTML = ''; // 清空旧内容
        container.appendChild(formatter.render()); // 渲染新内容
        
    });
    socket.on('new_message', function(message) {
        // 显示返回的所有消息，按顺序显示
        console.log(message)
        if (message.type === 'info') {
            var infoMessageHtml = '<div class="message info-message">' + message.content + '</div>';
            $('#messages').append(infoMessageHtml);
        } else if (message.type === 'response') {
            var responseMessageHtml = '<div class="message system-message">' + message.content;
            if (message.image) {
                responseMessageHtml += '<br><img src="' + message.image + '" alt="Image" class="chat-image" style="max-width: 100%; margin-top: 10px;">';
            }
            if (message.file_url && message.file_name) {
                responseMessageHtml += '<br><a href="' + message.file_url + '" download="' + message.file_name + '"><img src="/static/imgs/file_icon.png" alt="File" class="chat-file-icon" style="width: 20px; height: 20px; margin-top: 10px;"> ' + message.file_name + '</a>';
            }
            responseMessageHtml += '</div>';
            $('#messages').append(responseMessageHtml);
        }
        $('#messages').scrollTop($('#messages')[0].scrollHeight); // 自动滚动到底部
    });

    // 发送消息并处理按钮点击事件
    $('#send-button').click(function() {
        var message = $('#message-input').val();
        if (message.trim() !== '') {
            // 先显示用户的消息
            var userMessage = '<div class="message user-message">' + message + '</div>';
            $('#messages').append(userMessage);
            $('#message-input').val('');
            $('#messages').scrollTop($('#messages')[0].scrollHeight); // 自动滚动到底部

            // 使用 WebSocket 发送消息
            socket.send(message);
        }
    });
    // 心跳机制
    setInterval(function() {
        socket.emit('heartbeat', { data: 'heartbeat' });
    }, 150000); // 每 30 秒发送一次心跳

    // 监听 tab 的点击事件
    $('.tab').click(function() {
        var target = $(this).data('target');

        // 切换选中的 tab
        $('.tab').removeClass('active');
        $(this).addClass('active');

        // 切换显示的 tab 内容
        $('.tab-content').removeClass('active');
        $('#' + target).addClass('active');
        
        // 当切换到一个新的 network 时，重新初始化相应的网络图
        if (target === 'tab1') {
            console.log('plan');
        } else if (target === 'tab2') {
            console.log('code');
        } 
    });
});

