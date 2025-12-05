let sectionChoices, yearChoices, titleChoices;
let category = window.pageCategory;
let apiUrl = window.articlesApiUrl;  // URL passed from template

document.addEventListener("DOMContentLoaded", function () {

    sectionChoices = new Choices("#sectionSelect", {
        searchEnabled: true, itemSelectText: "", placeholderValue: "Select",
        removeItemButton: true, allowHTML: true
    });
    yearChoices = new Choices("#yearSelect", {
        searchEnabled: true, itemSelectText: "", placeholderValue: "Select",
        removeItemButton: true, allowHTML: true
    });
    titleChoices = new Choices("#titleSelect", {
        searchEnabled: true, itemSelectText: "", placeholderValue: "Select",
        removeItemButton: true, allowHTML: true
    });

    // Load titles (initial)
    $.getJSON(apiUrl, { mode: "getTitle", category }, function(response){
        titleChoices.setChoices(
            (response.titles || []).map(t => ({ value: t, label: t })),
            'value','label', true
        );
    });

    // Section changed
    $('#sectionSelect').on('change', function(){
        let selectedSection = $(this).val();
        if (!selectedSection) return;

        $.getJSON(apiUrl, { mode:"years", section:selectedSection, category }, function(response){
            yearChoices.clearStore();
            titleChoices.clearStore();

            yearChoices.setChoices(
                (response.years || []).map(y => ({ value: y, label: y })),
                'value','label', true
            );

            titleChoices.setChoices(
                (response.titles || []).map(t => ({ value: t, label: t })),
                'value','label', true
            );
        });
    });

    // Search
    $('#searchBtn').on('click', function(){
        let section = sectionChoices.getValue(true);
        let year = yearChoices.getValue(true);
        let title = titleChoices.getValue(true);
        let content = $('#search-content').val().trim();

        if (!section && !year && !title && !content) {
            Swal.fire({
                icon: 'warning',
                title: 'Oops!',
                text: 'Please type something or select filters to search.',
                confirmButtonColor: '#28a745'
            });
            return;
        }

        $.getJSON(apiUrl, { mode: "search", section, year, title, content, category }, function(response){
            renderResults(response);
        });
    });
});

function renderResults(response){
    let htmlArticles = '';
    let htmlRelated = '';
    const results = response.results || [];

    if (results.length){
        const first = results[0];
        htmlArticles = `<div class="card mb-3"><div class="card-body">
            <h4 class="card-title">${first.section} — ${first.title}</h4>
        </div></div>`;

        htmlRelated = `<table class="table table-bordered table-striped">
                        <thead>
                        <tr>
                            <th>ধারা</th>
                            <th style="width:80px;text-align:center;">করবর্ষ</th>
                            <th>বর্ণনা</th>
                        </tr>
                        </thead><tbody>`;

        results.forEach(item=>{
            htmlRelated += `<tr>
                <td><span class="text-danger">${item.section}</span></td>
                <td style="text-align:center;"><span class="text-danger">${item.assessment_year}</span></td>
                <td>${item.content}</td>
            </tr>`;
        });

        htmlRelated += '</tbody></table>';
    } else {
        htmlArticles = '<p class="text-muted">No articles found.</p>';
        htmlRelated = '<p class="text-muted">No related assessment content found.</p>';
    }

    $('#search-results').html(htmlArticles);
    $('#related-results').html(htmlRelated);

    if ($('#search-content').length)
        highlightText('#related-results', $('#search-content').val().trim());
}

function highlightText(containerSelector, text){
    if (!text) return;
    const container = document.querySelector(containerSelector);
    const escaped = text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(escaped, 'gi');
    container.innerHTML = container.innerHTML.replace(regex, m => `<span class="highlighted">${m}</span>`);
}
