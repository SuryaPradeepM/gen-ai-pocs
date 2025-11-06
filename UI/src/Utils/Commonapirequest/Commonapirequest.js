import axios from 'axios';
// application related URL
export const makeApiRequest = async (object) => {
    // below is for URL
    let endPointUrl = ( object.url)
    // below is for POST obj
    let Obj = (object.data == null ? "" : object.data)
    // below is for Method type
    let requestMethod = object.requestMethod
    let resolved = {
        data: null,
        error: null
    };
    console.log("OBJ>>>>", object)
    await axios({
        url: endPointUrl,
        method: requestMethod,
        data: Obj || "",
        responseType: (object.downLoadFileFlag ? 'blob' : 'json')
    }).then((response) => {
        
        resolved = response
    }).catch((error) => {
        resolved = error.response
    })
    return resolved;
}