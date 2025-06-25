function highlightBySelect(expanderIndex, selectedOption) {
    // 모든 textarea 초기화
    window.parent.document.querySelectorAll("textarea").forEach(t => {
        t.classList.remove("active-highlight");
    });

    const normalId = `minwon result_${expanderIndex}`;
    const ragId = `result_rag_${expanderIndex}`;

    const textarea1 = window.parent.document.querySelector(`textarea[id="${normalId}"]`);
    const textarea2 = window.parent.document.querySelector(`textarea[id="${ragId}"]`);

    if (selectedOption === "답변" && textarea1) {
        textarea1.classList.add("active-highlight");
    } else if (selectedOption === "답변(RAG)" && textarea2) {
        textarea2.classList.add("active-highlight");
    }
}