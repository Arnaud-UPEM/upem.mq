const Alerts = {
    open (e) {
        let target = e;
        while(!e.classList.contains('alerts')) {
            target = target.parentElement;
        }

        const type = e.getAttribute ('data-type');
        // const lifespan = e.getAttribute ('data-lifespan');
        const date_end = e.getAttribute ('data-date_end');
        const date_start = e.getAttribute ('data-date_start');
        const date_created = e.getAttribute ('data-date_created');

        const title = e.querySelector ('.alerts__title p').innerHTML;
        const content = e.querySelector ('.alerts__body').innerHTML;

        $('.ui.modal.alerts').modal('show');
        
        const modal = document.querySelector('.ui.modal.alerts');

        modal.className = 'ui modal small alerts ' + type;
        modal.querySelector ('.alerts__title p').innerHTML = title;
        modal.querySelector ('.alerts__body').innerHTML = content;

        modal.querySelector ('.meta .de').innerHTML = date_end;
        modal.querySelector ('.meta .ds').innerHTML = date_start;
        modal.querySelector ('.meta .dc').innerHTML = date_created;
        // modal.querySelector ('.meta .ls').innerHTML = lifespan;
    }


}