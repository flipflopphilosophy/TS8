document.addEventListener('DOMContentLoaded', function() {
    // Submit Form
    const submitForm = document.getElementById('submit-form');
    if (submitForm) {
        submitForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = {
                'type': document.getElementById('type').value,
                'text': document.getElementById('text').value
            };
            fetch('/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('response').innerHTML = '<div class="alert alert-success">Data submitted successfully!</div>';
            })
            .catch(error => {
                document.getElementById('response').innerHTML = '<div class="alert alert-danger">An error occurred.</div>';
                console.error('Error:', error);
            });
        });
    }

    // Filter Button
    const filterButton = document.getElementById('filter-button');
    if (filterButton) {
        filterButton.addEventListener('click', function() {
            const category = document.getElementById('filter-category').value;
            const startDate = document.getElementById('start-date').value;
            const endDate = document.getElementById('end-date').value;

            fetch(`/filtered_job_posts?category=${category}&start_date=${startDate}&end_date=${endDate}`)
                .then(response => response.json())
                .then(data => {
                    // Update the table with the filtered data
                    const tbody = document.querySelector('table tbody');
                    tbody.innerHTML = ''; // Clear existing rows

                    data.forEach(job => {
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td><input type="checkbox" name="job_id" value="${job[0]}"></td>
                            ${job.map(value => `<td>${value}</td>`).join('')}
                        `;
                        tbody.appendChild(row);
                    });
                })
                .catch(error => console.error('Error fetching filtered job posts:', error));
        });
    }

    // Resizable Columns
    const table = document.querySelector('table');
    if (table) {
        const headers = table.querySelectorAll('th.resizable');

        headers.forEach(header => {
            const resizer = document.createElement('div');
            resizer.classList.add('resizer');
            header.appendChild(resizer);
            resizer.addEventListener('mousedown', initResize);
        });

        function initResize(e) {
            const header = e.target.parentElement;
            const startX = e.clientX;
            const startWidth = header.offsetWidth;
            const index = Array.from(header.parentElement.children).indexOf(header);

            function resize(e) {
                const newWidth = startWidth + (e.clientX - startX);
                header.style.width = `${newWidth}px`;
                Array.from(table.querySelectorAll(`tr td:nth-child(${index + 1})`)).forEach(td => {
                    td.style.width = `${newWidth}px`;
                });
            }

            function stopResize() {
                document.removeEventListener('mousemove', resize);
                document.removeEventListener('mouseup', stopResize);
            }

            document.addEventListener('mousemove', resize);
            document.addEventListener('mouseup', stopResize);
        }
    }
});
