const Discord = require("discord.js"); //baixar a lib
const client = new Discord.Client(); 
const config = require("./config.json"); 
const axios = require('axios');


function get_args(str) {
  args = []

  var com = str.slice(0, str.indexOf(" ")).trim()
  var params = str.slice(str.indexOf(" ")).trim()

  console.log()
  if (com === "!ifood"){
    console.log("c")
    var params_list = params.split("/")
  }
  console.log("aa")
  console.log(params_list)
  var cc = {}

  for (param of params_list){
    var p = param.split("=")
    if(p[0] === "nota_minima"){
      cc[p[0]] = parseFloat(p[1].replace(/,/, '.'));
    } else if (p[0] === 'palavras_chave') {
      var keywords = []
      var k = p[1].replace(/\[/g, '').replace(/\]/g, '').split(',')
      for (x of k){
        keywords.push(x.trim())
      }
      cc[p[0]] = keywords
    } else if (p[0] === 'num_resultados') {
      cc[p[0]] =  parseInt(p[1]);
    } else {
      cc[p[0]] = p[1]
    }  
  }
  return cc
}


client.on("ready", () => {
  console.log(`Bot foi iniciado, com ${client.users.size} usuários, em ${client.channels.size} canais, em ${client.guilds.size} servidores.`); 
});

client.on("message", async message => {

    if(message.author.bot) return;
    if(message.channel.type === "dm") return;
    if(!message.content.startsWith(config.prefix)) return;

    console.log(message.content);
    //const args = message.content.slice(config.prefix.length).trim();
    //const comando = args.shift().toLowerCase();
    
    console.log("request");
    var response = await axios.post("http://localhost:5000/ifood/", get_args(message.content))

    var m = await message.channel.send("---------------------------------------------------------");
    var final_str = ""
    var num = response['data'].length
    var max = 0
    if (num > 15)
    {
      max = 15
    } else {
      max = num
    }
    for (var i = 0; i < max; i++)
    {
      final_str += response['data'][i] + " \n";
    }
    if (final_str.length == 0) {
      var m = await message.channel.send("nenhum resultado encontrado :((");
    } else {
      var m = await message.channel.send(final_str.slice(0, 2000));
    }

    
  
});

client.login(config.token);
