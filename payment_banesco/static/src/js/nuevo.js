_onCLickBanesco: function(env){
    let id = $("table[idref]").attr('idref')
    let arrTokenId = id.split("O")
    const values = {"token":arrTokenId[0],"invoice_id":arrTokenId[1],"banesco":1}
    const url2 = "/search/amount/invoice"
    
    async function hmacSha256(message, secret) {
        // codificar como UTF-8
        const msgBuffer = new TextEncoder().encode(message);
        const keyBuffer = new TextEncoder().encode(secret);
        // importar la clave secreta
        const key = await crypto.subtle.importKey('raw', keyBuffer, { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
        // encriptar el mensaje
        const signature = await crypto.subtle.sign('HMAC', key, msgBuffer);
        // convertir ArrayBuffer a Array
        const hashArray = Array.from(new Uint8Array(signature));
        // convertir bytes a cadena hexadecimal
        const hashHex = hashArray.map(b => ('00' + b.toString(16)).slice(-2)).join('');
        return hashHex;
    }

    // let valor5 = "Licencia Original"; //---- Descripción o concepto del trámite
    const modalBanesco = async (promise,result_data) =>{
        let firma;
        let url = "https://qa-botondepago.banescopagos.com";
        let dinamic_camp = result_data.instance+"|"+result_data.taxpayer;
        try{
            firma = await promise;
        }catch(error){
            console.log(error);
        }
        banesco.Banesco_open_win(url,
            '',
            result_data.subtotal.toString(),
            dinamic_camp,
            result_data.ai_id,
            result_data.reference,
            result_data.api_key,
            firma,
            1
            );
        }
        // console.log(dinamic_camp,'Aqui vamos a mandar el post al micro para probar');
        ajax.post(url2,values)
        .then(function(result_data){ 
            result_data = $.parseJSON(result_data)
            
            let dinamic_camp = result_data.instance+"|"+result_data.taxpayer;
            let firmar = result_data.api_key+result_data.rif+result_data.subtotal.toString()+dinamic_camp+result_data.ai_id;
            console.log(firmar);
            let firma= {"firmar":firmar,"secret":result_data.secret}
            // ajax.post('/hash/send/payment',firma)
            // .then(function(result_data){result_data})
            let cFirma = hmacSha256(firmar,result_data.secret)  
            
            modalBanesco(cFirma,result_data)
    })
}