/**
 * Production AI Assistant JavaScript Handler
 * Connects to Backend AI API, renders validated results with strict safety.
 */

let currentMode = 'progress_summary';

function switchMode(mode) {
    currentMode = mode;
    document.getElementById('selectedMode').value = mode;

    // Update tab styling
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.mode === mode);
    });

    // Update form controls based on mode
    const orderGroup = document.getElementById('orderFilterGroup');
    const limitGroup = document.getElementById('suggestionLimitGroup');
    const promptInput = document.getElementById('aiPromptText');

    if (mode === 'order_priority') {
        orderGroup.style.display = 'none';
        limitGroup.style.display = 'block';
        promptInput.placeholder = 'Gợi ý các đơn cần ưu tiên dựa trên hạn giao và vật tư khả dụng...';
    } else if (mode === 'defect_analysis') {
        orderGroup.style.display = 'block';
        limitGroup.style.display = 'none';
        promptInput.placeholder = 'Phân tích các lỗi phát sinh của đơn này và gom nhóm nguyên nhân...';
    } else {
        orderGroup.style.display = 'block';
        limitGroup.style.display = 'none';
        promptInput.placeholder = 'Tóm tắt tiến độ đơn và các công đoạn có nguy cơ chậm...';
    }

    // Toggle quick suggestion chips
    document.querySelectorAll('.ai-quick-chip').forEach(chip => {
        chip.style.display = chip.dataset.mode === mode ? 'inline-flex' : 'none';
    });

    // Hide previous result
    document.getElementById('aiResultCard').style.display = 'none';
}

async function submitAITask() {
    const loading = document.getElementById('aiLoadingIndicator');
    const resultCard = document.getElementById('aiResultCard');
    const orderSelect = document.getElementById('aiOrderSelect');
    const promptText = document.getElementById('aiPromptText').value;
    const maxSug = document.getElementById('maxSuggestions').value;

    loading.style.display = 'block';
    resultCard.style.display = 'none';

    let endpoint = '/api/ai/progress-summary';
    let payload = { prompt: promptText };

    if (currentMode === 'defect_analysis') {
        endpoint = '/api/ai/defect-analysis';
        payload.order_id = orderSelect.value;
    } else if (currentMode === 'order_priority') {
        endpoint = '/api/ai/order-priority';
        payload.max_suggestions = maxSug;
    } else {
        payload.order_id = orderSelect.value;
    }

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').content
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        renderAIResponse(data);
    } catch (err) {
        alert('Lỗi kết nối máy chủ hoặc API: ' + err.message);
    } finally {
        loading.style.display = 'none';
    }
}

function renderAIResponse(data) {
    const resultCard = document.getElementById('aiResultCard');
    const summaryText = document.getElementById('aiSummaryContent');
    const factsContainer = document.getElementById('aiFactsContainer');
    const dynamicSection = document.getElementById('aiDynamicSection');
    const sourceIdsContainer = document.getElementById('aiSourceIds');
    const statusBadge = document.getElementById('resultStatusBadge');
    const humanBox = document.getElementById('humanActionBox');

    resultCard.style.display = 'block';

    // Status badge
    if (data.status === 'ok') {
        statusBadge.className = 'badge badge-success';
        statusBadge.innerText = 'ĐÃ XÁC MINH';
    } else if (data.status === 'no_data') {
        statusBadge.className = 'badge badge-warning';
        statusBadge.innerText = 'KHÔNG CÓ DỮ LIỆU';
    } else {
        statusBadge.className = 'badge badge-danger';
        statusBadge.innerText = 'CẦN KIỂM TRA (NEEDS REVIEW)';
    }

    // Summary text
    summaryText.innerText = data.summary || 'Không có bản tóm tắt';
    document.getElementById('aiProvider').innerText = data.provider === 'gemini'
        ? 'Nguồn xử lý: Gemini (đã đối chiếu dữ liệu nguồn)'
        : 'Nguồn xử lý: quy tắc cục bộ; chưa gọi Gemini';

    // Facts
    factsContainer.innerHTML = '';
    const facts = data.facts || {};
    for (const [k, v] of Object.entries(facts)) {
        const factCard = document.createElement('div');
        factCard.className = 'fact-card';
        factCard.innerHTML = `<div class="fact-title">${escapeHTML(k)}</div><div class="fact-val">${escapeHTML(String(v))}</div>`;
        factsContainer.appendChild(factCard);
    }

    // Dynamic section: Defect hypotheses or Recommendations
    dynamicSection.innerHTML = '';

    if (data.task_type === 'defect_analysis' && data.hypotheses) {
        const hypTitle = document.createElement('h5');
        hypTitle.innerHTML = '<i class="fa-solid fa-lightbulb text-warning"></i> Giả thuyết nguyên nhân kỹ thuật do AI đề xuất:';
        dynamicSection.appendChild(hypTitle);

        data.hypotheses.forEach(h => {
            const item = document.createElement('div');
            item.className = 'hypothesis-item';
            item.innerHTML = `<i class="fa-solid fa-flask"></i> ${escapeHTML(h)}`;
            dynamicSection.appendChild(item);
        });
    } else if (data.task_type === 'order_priority' && data.recommendations) {
        const recTitle = document.createElement('h5');
        recTitle.innerHTML = '<i class="fa-solid fa-ranking-star text-primary"></i> Đề xuất thứ tự ưu tiên sản xuất:';
        dynamicSection.appendChild(recTitle);

        data.recommendations.forEach(r => {
            const item = document.createElement('div');
            item.className = 'recommendation-card';
            item.innerHTML = `
                <div style="display: flex; align-items: center;">
                    <div class="rec-rank">#${escapeHTML(String(r.rank))}</div>
                    <div>
                        <strong>Đơn #${escapeHTML(String(r.order_id))}: ${escapeHTML(r.product_name)}</strong>
                        <div class="text-muted small">${escapeHTML(r.reason)}</div>
                    </div>
                </div>
                <div>
                    <span class="badge ${r.material_constraint.includes('Thiếu') ? 'badge-danger' : 'badge-success'}">
                        ${escapeHTML(r.material_constraint)}
                    </span>
                </div>
            `;
            dynamicSection.appendChild(item);
        });

        if (humanBox) humanBox.style.display = data.status === 'ok' ? 'flex' : 'none';
    } else {
        if (humanBox) humanBox.style.display = 'none';
    }

    // Source IDs
    sourceIdsContainer.innerHTML = '';
    const sources = data.source_ids || [];
    if (sources.length > 0) {
        sources.forEach(s => {
            const b = document.createElement('span');
            b.className = 'source-badge';
            b.innerText = s;
            sourceIdsContainer.appendChild(b);
        });
    } else {
        sourceIdsContainer.innerHTML = '<span class="text-muted small italic">Không có mã nguồn</span>';
    }

    // Scroll to result
    resultCard.scrollIntoView({ behavior: 'smooth' });
}

function escapeHTML(str) {
    if (!str) return '';
    return str.replace(/[&<>'"]/g, 
        tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag] || tag)
    );
}

// Quick Prompt Chips Event Handling
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.ai-quick-chip').forEach(chip => {
        chip.addEventListener('click', function () {
            const promptInput = document.getElementById('aiPromptText');
            if (promptInput) {
                promptInput.value = this.dataset.prompt;
                promptInput.focus();
            }
        });
    });
});
