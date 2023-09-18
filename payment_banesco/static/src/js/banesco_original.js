odoo.define('tax_customer.receiptPaymentBanesco', function (require){
    'use strict';
    var ajax = require('web.ajax');

    const Banesco_body = document.querySelector('body');
    const Banesco_overlayDiv = document.createElement('div');
    let Banesco_displayBool = false;

    Banesco_overlayDiv.style.position = 'fixed';
    Banesco_overlayDiv.style.width = '100%';
    Banesco_overlayDiv.style.height = '100%';
    Banesco_overlayDiv.style.top = '0';
    Banesco_overlayDiv.style.left = '0';
    Banesco_overlayDiv.style.right = '0';
    Banesco_overlayDiv.style.bottom = '0';
    Banesco_overlayDiv.style.backgroundColor = 'rgba(0,0,0,0.5)';
    Banesco_overlayDiv.style.zIndex = '2';
    Banesco_overlayDiv.style.textAlign = '-webkit-center';
    Banesco_overlayDiv.style.display = "none";

    function Banesco_styleOverlay() {
        const Banesco_contentContainer = document.querySelector('#Banesco_DIVIframe');
        Banesco_contentContainer.style.textAlign = 'center';
        Banesco_contentContainer.style.marginTop = '0';
        Banesco_contentContainer.style.backgroundColor = '#5f685c';
        Banesco_contentContainer.style.width = '100%';
        Banesco_contentContainer.style.height = '100%';
        Banesco_contentContainer.style.display = 'block';
        Banesco_contentContainer.style.zIndex = '99999999999999';
        Banesco_contentContainer.style.position = 'fixed';
        Banesco_contentContainer.style.opacity = '1';
    }

    function Banesco_Cancelar(event) {
        if (event.origin !== "https://localhost:5001")
            return;

        if (event.data == "banesco_pago_completo" || event.data == "banesco_cancelar") {
            banesco_iframe = document.getElementById("Banesco_DIVIframe");
            document.body.removeChild(banesco_iframe);
            window.removeEventListener("message", Banesco_Cancelar, false);
        }
    }

    // function Banesco_Cancelar2(event) {
        
    //     var datos=event.data;
    //     if (datos != "") {
    //         const cmd = datos.split("|");
    //         if(cmd.length>=2)
    //         {
    //         switch(cmd[0]) {
    //             case "r":
    //             window.location.href=cmd[1];
    //             break;			  
    //         }
    //         }
    //     }
    // }

    function Banesco_boton(url, cedula, monto, idtramite, comprobante, concepto, apikey, firma, tipo) {
        if ( idtramite.length <= 32 && comprobante.length <= 22 && concepto.length <= 60 && cedula.length <= 10 && monto.length <= 17 ) {
            return `<img id='banesco_img_boton' src='data:image/gif;base64, ` + _BOTON_ + `'  onclick='Banesco_open_win("` + url + `","`
                + cedula + `","` + monto + `","`
                + idtramite + `","` + comprobante + `","`
                + concepto + `","` + apikey + `","`
                + firma + `", 1 )'>`;
        } else {
            return "<span>Error en datos </span>"
        };
    }
    function Banesco_open_win(url, cedula, monto, idtramite, comprobante, concepto, apikey, firma, tipo)	 {
        if (tipo == 1) {
            // window.addEventListener("message", Banesco_Cancelar, false);
            let Banesco_window = window.open("Boton de Pago Banesco", "Banesco_Boton", "dialog=yes,status=no,toolbar=no,location=no,menubar=no,scrollbars=no,resizable=no,fullscreen=no,height=" + (screen.height * 0.8) + "px, width = 465px");
            //var loading= _LOADING_;
            var html = "<div style='background-color:#00795354;height:100%;'><div style='top:50%;left:35%;position:absolute;'><img src='data:image/gif;base64, " + _LOADING_ + "' /><br><span>Conectando ...</span></div></div>";
            Banesco_window.document.write(html);
            //Hidden Form
            var banesco_form = document.createElement("form");
            banesco_form.setAttribute("method", "post");
            banesco_form.setAttribute("action", url);
            banesco_form.setAttribute("target", "Banesco_Boton");

            //Hidden Field
            var banesco_formhiddenField1 = document.createElement("input");
            var banesco_formhiddenField2 = document.createElement("input");
            var banesco_formhiddenField3 = document.createElement("input");
            var banesco_formhiddenField4 = document.createElement("input");
            var banesco_formhiddenField5 = document.createElement("input");
            var banesco_formhiddenField6 = document.createElement("input");
            var banesco_formhiddenField7 = document.createElement("input");
            var banesco_formhiddenField8 = document.createElement("input");

            //cedula
            banesco_formhiddenField1.setAttribute("type", "hidden");
            banesco_formhiddenField1.setAttribute("id", "valor1");
            banesco_formhiddenField1.setAttribute("name", "valor1");
            banesco_formhiddenField1.setAttribute("value", cedula);
            //monto
            banesco_formhiddenField2.setAttribute("type", "hidden");
            banesco_formhiddenField2.setAttribute("id", "valor2");
            banesco_formhiddenField2.setAttribute("name", "valor2");
            banesco_formhiddenField2.setAttribute("value", monto);

            //idtramite
            banesco_formhiddenField3.setAttribute("type", "hidden");
            banesco_formhiddenField3.setAttribute("id", "valor3");
            banesco_formhiddenField3.setAttribute("name", "valor3");
            banesco_formhiddenField3.setAttribute("value", idtramite);

            //comprobante
            banesco_formhiddenField4.setAttribute("type", "hidden");
            banesco_formhiddenField4.setAttribute("id", "valor4");
            banesco_formhiddenField4.setAttribute("name", "valor4");
            banesco_formhiddenField4.setAttribute("value", comprobante);

            //concepto
            banesco_formhiddenField5.setAttribute("type", "hidden");
            banesco_formhiddenField5.setAttribute("id", "valor5");
            banesco_formhiddenField5.setAttribute("name", "valor5");
            banesco_formhiddenField5.setAttribute("value", concepto);

            //apikey
            banesco_formhiddenField6.setAttribute("type", "hidden");
            banesco_formhiddenField6.setAttribute("id", "apikey");
            banesco_formhiddenField6.setAttribute("name", "apikey");
            banesco_formhiddenField6.setAttribute("value", apikey);

            //firma
            banesco_formhiddenField7.setAttribute("type", "hidden");
            banesco_formhiddenField7.setAttribute("id", "firma");
            banesco_formhiddenField7.setAttribute("name", "firma");
            banesco_formhiddenField7.setAttribute("value", firma);

            //tipo
            banesco_formhiddenField8.setAttribute("type", "hidden");
            banesco_formhiddenField8.setAttribute("id", "tipo");
            banesco_formhiddenField8.setAttribute("name", "tipo");
            banesco_formhiddenField8.setAttribute("value", tipo);


            banesco_form.appendChild(banesco_formhiddenField1);
            banesco_form.appendChild(banesco_formhiddenField2);
            banesco_form.appendChild(banesco_formhiddenField3);
            banesco_form.appendChild(banesco_formhiddenField4);
            banesco_form.appendChild(banesco_formhiddenField5);
            banesco_form.appendChild(banesco_formhiddenField6);
            banesco_form.appendChild(banesco_formhiddenField7);
            banesco_form.appendChild(banesco_formhiddenField8);

            document.body.appendChild(banesco_form);
            banesco_form.submit();
        }
        else {
            window.addEventListener("message", Banesco_Cancelar, false);
            var params = "cedula=" + cedula;
            params += "&firma=" + firma;
            params += "&monto=" + monto;
            params += "&idtramite=" + idtramite;
            params += "&comprobante=" + comprobante;
            params += "&concepto=" + concepto;
            params += "&apikey=" + apikey;
            params += "&tipo=" + tipo;
            params = "?" + params;

            var banesco_div = document.createElement("div");
            banesco_div.setAttribute("id", "Banesco_DIVIframe");
            banesco_div.setAttribute("position", "relative");
            banesco_div.setAttribute("style", "background-color: rgba(255,255,255,.5)");

            var banesco_iframe = document.createElement("iframe");
            banesco_iframe.setAttribute("id", "Banesco_Iframe");
            banesco_iframe.setAttribute("src", url + params);
            banesco_iframe.setAttribute("title", "Boton de pagos Banesco ");
            banesco_iframe.setAttribute("width", "60%");
            banesco_iframe.setAttribute("height", "70%");
            banesco_iframe.setAttribute("allow", "payment");
            banesco_iframe.setAttribute("scrolling", "no");
            banesco_iframe.setAttribute("style", " margin-top : 15px");

            banesco_div.appendChild(banesco_iframe);

            document.body.appendChild(banesco_div);
            document.body.prepend(banesco_div);
            Banesco_styleOverlay();
        }


    }
    return {
        Banesco_boton:Banesco_boton,
        Banesco_open_win:Banesco_open_win
    }
})
