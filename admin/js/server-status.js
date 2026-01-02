/**
 * Server Status Details Modal
 * Shows detailed information about server health
 */

window.showServerStatusDetails = function() {
    const data = window.serverStatusData || { servers: [] };
    
    // Create modal
    const modal = document.createElement('div');
    modal.id = 'serverStatusModal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.8);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
    `;
    
    const modalContent = document.createElement('div');
    modalContent.style.cssText = `
        background: #1A1A1A;
        border: 1px solid #333333;
        border-radius: 12px;
        padding: 30px;
        max-width: 800px;
        width: 100%;
        max-height: 90vh;
        overflow-y: auto;
        color: #FFFFFF;
    `;
    
    let serversHTML = '';
    if (data.servers && data.servers.length > 0) {
        serversHTML = data.servers.map(server => {
            let statusColor = '#00FF85';
            let statusIcon = '✓';
            if (server.status === 'down') {
                statusColor = '#FF4444';
                statusIcon = '✗';
            } else if (server.status === 'degraded') {
                statusColor = '#FFD600';
                statusIcon = '⚠';
            }
            
            return `
                <div style="padding: 20px; background: #2A2A2A; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid ${statusColor};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                        <h3 style="color: #FFFFFF; margin: 0; font-size: 18px;">${server.name || server.server}</h3>
                        <span style="color: ${statusColor}; font-weight: 600; font-size: 14px;">
                            ${statusIcon} ${server.status ? server.status.toUpperCase() : 'UNKNOWN'}
                        </span>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px;">
                        <div>
                            <div style="color: #B0B0B0; font-size: 12px; margin-bottom: 5px;">API Status</div>
                            <div style="color: ${server.api_status === 'healthy' ? '#00FF85' : server.api_status === 'down' ? '#FF4444' : '#FFD600'}; font-weight: 600;">
                                ${server.api_status ? server.api_status.toUpperCase() : 'UNKNOWN'}
                            </div>
                            ${server.api_error ? `<div style="color: #FF4444; font-size: 11px; margin-top: 5px;">${server.api_error}</div>` : ''}
                            ${server.api_response_time ? `<div style="color: #888; font-size: 11px; margin-top: 5px;">Response: ${server.api_response_time}ms</div>` : ''}
                        </div>
                        <div>
                            <div style="color: #B0B0B0; font-size: 12px; margin-bottom: 5px;">Website Status</div>
                            <div style="color: ${server.website_status === 'healthy' ? '#00FF85' : server.website_status === 'down' ? '#FF4444' : '#FFD600'}; font-weight: 600;">
                                ${server.website_status ? server.website_status.toUpperCase() : 'UNKNOWN'}
                            </div>
                            ${server.website_error ? `<div style="color: #FF4444; font-size: 11px; margin-top: 5px;">${server.website_error}</div>` : ''}
                            ${server.website_response_time ? `<div style="color: #888; font-size: 11px; margin-top: 5px;">Response: ${server.website_response_time}ms</div>` : ''}
                        </div>
                    </div>
                    ${server.timestamp ? `<div style="color: #666; font-size: 11px; margin-top: 10px;">Last checked: ${new Date(server.timestamp).toLocaleString()}</div>` : ''}
                </div>
            `;
        }).join('');
    } else {
        serversHTML = '<div style="text-align: center; padding: 40px; color: #B0B0B0;">No server data available</div>';
    }
    
    modalContent.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px;">
            <h2 style="color: #00FF85; margin: 0; font-size: 24px;">Server Status</h2>
            <button onclick="document.getElementById('serverStatusModal').remove()" style="
                background: transparent;
                border: none;
                color: #B0B0B0;
                font-size: 24px;
                cursor: pointer;
                padding: 0;
                width: 30px;
                height: 30px;
                display: flex;
                align-items: center;
                justify-content: center;
            ">×</button>
        </div>
        <div style="margin-bottom: 20px;">
            ${serversHTML}
        </div>
        <div style="text-align: center; margin-top: 20px;">
            <button onclick="document.getElementById('serverStatusModal').remove()" style="
                background: #00FF85;
                color: #1A1A1A;
                border: none;
                padding: 12px 32px;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 600;
                font-size: 14px;
            ">Close</button>
        </div>
    `;
    
    modal.appendChild(modalContent);
    document.body.appendChild(modal);
    
    // Close on background click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
};

// Add CSS animation for pulse effect
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }
`;
document.head.appendChild(style);

