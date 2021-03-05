/*
  QUBO-P - 20 Buttons Version with RGB LED and send toggle information
 
 
  Omar Abdulaaty - May 2020
  omar.abdulaaty@tu-dortmund.de
  TU Dortmund LS8 
  
  Last edited: March 2021 - With Toggle and contrain fitness function
  
 */


// initialize the library with the numbers of the interface pins

const int buttonPins[] = {18,19,6,7,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52}; // the number of the pushbutton pin for input states
const int ledPins[]    = {23,25,27,29,31,33,35,37,39,41,43,45,47,49,51,53,17,16,15,14};  
const int rbgOutput[] = {2,5,3};
#define receivedByteLength 2

//const int autoSolButton = 13; // For the automatic solution
#define autoSolButton 13


//const int size_of_problem =(sizeof(buttonPins) / sizeof(buttonPins[0]) ) ;
#define size_of_problem (sizeof(buttonPins)/sizeof(buttonPins[0])) 

//Button debounce delay
#define timeOfDelay 50

//Delay to show red or green after evalutaion
#define fitnessEvalVisualDelay 500
//Auto mode animation delay
int timeOfdelayForAuto = 100;
//Auto mode animation number of iterations
int numOfIterations = 50;
//Config mode delay
#define timeOfdelayForConfig 50
//a variable to read incoming serial data
byte incomingByte;

//Values to indicate the current state, fitness 
//and a flag for any pressed button

int state[size_of_problem];
int current_state; //temp for delay

int fitness = 0;
int fitnessScaled = 0;
int fintessPrev = 0;
int autoModeIndicator = 0;
int changedState = 0;


//RGB Led Output

int Red   = 0;
int Green = 0;


//flag for 
int autoStateEnable=0;


//The Following remaining values should be changed for each separate
// set of values of Weight Matrix


// Weight Matrix
int weightMatrix[ size_of_problem ][ size_of_problem ] = 
{{ -79,  -31,  139,   19,  -77,  -26,  -55,  -67,   83,  118, -116,    3,   -50, -116,  -38, -100,   73,  109,  -97,  103},
 {   0, -106, -172,   23,  179,   -1, -155,  116,  169, -147, -116, -172,  -180,  -12, -155,   31, -118,  -47, -108,   94},
 {   0,    0,  138,   65,   13, -171,  -91,  162, -170,  145, -112,  165,    73,  131,  156,  104,   89,  160,  179, -146},
 {   0,    0,    0,   42,  -16,  -74,   25, -163,  -92, -101, -137,  -54,  -155, -112,   73,  133,   80,  -97,  102,  -79},
 {   0,    0,    0,    0, -170,  135,   15,  162, -110,   91, -147, -102,   -88,   93,  110, -110,  167,  116,   47,  100},
 {   0,    0,    0,    0,    0,   17,  -55,   35,   98,   94,   58,  116,   153,  131,    7,  105,  -47,  -15, -164,   82},
 {   0,    0,    0,    0,    0,    0,  -19,   29,   48,  -41,   92,  159,   -32,  114,   71, -119,  -61,  -22,  122,  -91},
 {   0,    0,    0,    0,    0,    0,    0,   61,  107,   21,  123,   13,     3,  170,    4, -178,  175,  128,  -33,   64},
 {   0,    0,    0,    0,    0,    0,    0,    0,  132,  -76, -133,  114,  -142,  166,  -49,  143,  -93,    9,   85,    9},
 {   0,    0,    0,    0,    0,    0,    0,    0,    0,   92,  -92,  -62,   -79,  -42,  136,  140, -159,  -76,   15, -123},
 {   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,  109,   91,   -94, -156,  101,   85,   99,   51,   28,  149},
 {   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0, -140,   159, -115,  162,  -36,   69,   96,  -95,  168},
 {   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,   -61,  164, -148,  174, -159,  176,  -86,  157},
 {   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,     0,  -75,  144,  134, -108,   72, -158,  160},
 {   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,     0,    0,  -90,   60,  175, -163, -137,   90},
 {   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,     0,    0,    0,  117,  119,  -32,   82,   79},
 {   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,     0,    0,    0,    0, -127,  -32,  -81,  -28},
 {   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,     0,    0,    0,    0,    0,  108,   53, -156},
 {   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,     0,    0,    0,    0,    0,    0,  -96,  139},
 {   0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,     0,    0,    0,    0,    0,    0,    0,   10}};

int minValueOfFitness = -2729*2;
//#define minValueOfFitness -2729
 int rangeOfFitnessValue = 6639*2;
//#define rangeOfFitnessValue 6639
//#define MaxOutputPWM 255
int MaxOutputPWM = 255; 
 
//Solution Space
int solPosSpace[size_of_problem] = {0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1};
//#define size_of_solution_High (sizeof(solPosSpace)/sizeof(solPosSpace[0])) 
//const int solNegSpace[] = {0,1};
//#define size_of_solution_Low (sizeof(solNegSpace)/sizeof(solNegSpace[0])) 


  
void setup() {
  // initialize serial communication:
    Serial.begin(9600);
    while (!Serial) {
    ; // wait for serial port to connect. Needed for Native USB only
    }
  //Input Leds initialization
    for (int i = 0; i <size_of_problem; i++) {
     pinMode(buttonPins[i], INPUT);
    }
  //Output Leds initialization
  for (int j = 0; j <size_of_problem; j++) {
      pinMode(ledPins[j], OUTPUT);
    }

  //Output RGB Led initialization
    pinMode(rbgOutput[0], OUTPUT);
    pinMode(rbgOutput[1], OUTPUT);
    pinMode(rbgOutput[2], OUTPUT);
     
  //Input auto solution button
    pinMode(autoSolButton, INPUT);

  
    scaleFitness();
}


void loop() {

 if (Serial.available()>0) {
   ConfigMode();
  
  } 
  

 autoStateEnable =digitalRead(autoSolButton);
  if (autoStateEnable == HIGH){
    //delay(timeOfDelay); //will be used for debouncing in hardware
    autoSolMode();
  }

  for (int i = 0; i <size_of_problem; i++) {
     
        
       current_state = digitalRead(buttonPins[i]);
      
      if( current_state == 1) {
      
        state[i] =  Digital_Button_Read(i);
       

        if(changedState == 1){
        updateFitness();
        scaleFitness();
        }
        
      }
  }
  
 
      //analogWrite(rbgOutput[0], Red);
      //analogWrite(rbgOutput[2], Green);

  
  
 
}


 int Digital_Button_Read(int index){
  delay(timeOfDelay); //will be used for debouncing in hardware
  int r = digitalRead(buttonPins[index]);
  if(r ==1){
     r = !digitalRead(ledPins[index]);
    while(digitalRead(buttonPins[index]));
      
        
     changedState = 1;
     digitalWrite(ledPins[index], !digitalRead(ledPins[index]) ); 
     toggle(index);
  }
   return r;
 }


void updateFitness(){
  //x'Mx 
  // inner loop c = Mx
  // outer loop fitness = x'c
  int c[size_of_problem];
  fintessPrev = fitness;
  fitness = 0;
  for (int i = 0; i < size_of_problem; i++){
    c[i] = 0 ;
    for (int j = 0; j < size_of_problem; j++){
      if(weightMatrix[i][j] == 0){
        c[i] += weightMatrix[j][i]*state[j];
      }
      else
      {
        c[i] += weightMatrix[i][j]*state[j];
      }
  
    }
    fitness += c[i]*state[i];
    
  } 
  changedState = 0;
}

void scaleFitness(){

fitnessScaled = ((double)(fitness-minValueOfFitness)/(rangeOfFitnessValue))*MaxOutputPWM;
fitnessScaled = constrain(fitnessScaled,0,255);
//Serial.println(fitnessScaled);
Red = MaxOutputPWM - fitnessScaled;
Green = fitnessScaled; 
  if(!autoModeIndicator){
  if(fintessPrev > fitness){
    analogWrite(rbgOutput[0], MaxOutputPWM);
   analogWrite(rbgOutput[2], 0);
    
  }else if(fintessPrev <= fitness){
    analogWrite(rbgOutput[0], 0);
   analogWrite(rbgOutput[2], MaxOutputPWM);
  }  
  delay(fitnessEvalVisualDelay);
  
  
}
   analogWrite(rbgOutput[0], Red);
   analogWrite(rbgOutput[2], Green);
}


void autoSolMode(){
 int randNumber1;
 autoModeIndicator = 1; 
  for (int i = 0; i <numOfIterations; i++ ){
  
    for (int k = 0; k <size_of_problem; k++){
      
      randNumber1 = random(100);
      if(   randNumber1%2 == 0){
        state[k] = !digitalRead(ledPins[k]);
        digitalWrite(ledPins[k], !digitalRead(ledPins[k]) ); 

      }
    }
   
  updateFitness();
  scaleFitness();
  
  delay(timeOfdelayForAuto);
  }
  

 
  for(int l =0; l<size_of_problem; l++){
  state[l] = 0;
  digitalWrite(ledPins[l], LOW );
  }
  
  for(int h =0; h<size_of_problem; h++){
  state[h] = solPosSpace[h];
  if(solPosSpace[h] == 1){
    digitalWrite(ledPins[h], HIGH );
  }
  else 
  {
    digitalWrite(ledPins[h], LOW );

  }
  
  }
  
 
 updateFitness();
 scaleFitness();
 autoModeIndicator = 0; 


}

void toggle(int index){
     Serial.println(index);
     Serial.flush();
     delay(timeOfdelayForConfig);
     return;
  
}


void ConfigMode(){
  
 incomingByte =Serial.read(); 
/*
  Protocool 
  S ==> Start Matrix transmission (client to arduino)
  A ==> Auto solution mode
  G ==> send Matrix client (arduino to clinet)
  B ==> send Buttons status  (arduino to clinet)
  K ==> get buttons status (client to arduino)
  D ==> auto solution mode with delay
  U ==> blink hint


  Q ==> error signal (arduino to clinet)
 */
 if(incomingByte == 'S'){
   receive_parameters();
 }
 else 
 {
    if(incomingByte == 'A'){
     Serial.write("a\n");
     Serial.flush();
     autoSolMode_V2();
     Serial.write("!\n");
     Serial.flush();
    // delay(timeOfdelayForConfig);
    }
    else 
    {
      if(incomingByte == 'G'){
      send_parameters();
      }
      else
      {
        if(incomingByte == 'B'){
        send_buttons_status();
        }
        else
        {
         if(incomingByte == 'K'){
          set_buttons_status();
         }
         else
         {
          if(incomingByte == 'D'){
           auto_mode_with_delay();
          }
          else
          {
            if(incomingByte == 'U'){
              blink_hint();
            }
            else
            {
              Serial.write("q\n");
              Serial.flush();
              //delay(timeOfdelayForConfig);
            }
          }
         }
        }
      }
    }
 }
  updateFitness();
  scaleFitness();  
}

void receive_parameters(){
  
    Serial.write("s\n");
    Serial.flush();
    int num;
    unsigned char bufferL[receivedByteLength];
    int readNum =0;
    int curr_col = 0;
    int curr_row = 0;
  
    do {
      while(Serial.available()<=0){}
      num = Serial.readBytes(bufferL, receivedByteLength);
      readNum =  (bufferL[0] << 8) | bufferL[1];
      weightMatrix[curr_row][curr_col] = readNum;
      weightMatrix[curr_col][curr_row] = readNum;
      curr_col++;
      if (curr_col >= size_of_problem){
        curr_row++;
        curr_col = curr_row;
      }
      Serial.println(readNum);
      bufferL[0] = 0;
      bufferL[1] = 0;
      bufferL[2] = 0;
      readNum = 0;
    } while (curr_row< size_of_problem);   //count<((size_of_problem)*(size_of_problem+1)/2)
   
    Serial.write("!\n");
    Serial.flush();
    int solCount = 0;

    do {
      while(Serial.available()<=0){}
      num = Serial.readBytes(bufferL, receivedByteLength);
      Serial.read();
      readNum =  (bufferL[0] << 8) | bufferL[1];
      solPosSpace[solCount] = readNum;
      Serial.println(readNum);
      Serial.flush();
      solCount++;
      
    } while (solCount< size_of_problem);

    //Recieve min value
    while(Serial.available()<=0){} 
    num = Serial.readBytes(bufferL, receivedByteLength);
    Serial.read();
    readNum =  (bufferL[0] << 8) | bufferL[1];
    minValueOfFitness = readNum*2;
    Serial.println(readNum);
    Serial.flush();

    //Recieve values range
    while(Serial.available()<=0){}
    num = Serial.readBytes(bufferL, receivedByteLength);
    Serial.read();
    readNum =  (bufferL[0] << 8) | bufferL[1];
    rangeOfFitnessValue = readNum*2;
    Serial.println(readNum);
    Serial.flush();


      
    Serial.write("!\n");
    Serial.flush();
  }



void send_parameters(){
  Serial.write("g\n");
  Serial.flush();

 
  int curr_col = 0;
  int curr_row = 0;
  while (curr_row< size_of_problem) {
        
    Serial.println(weightMatrix[curr_row][curr_col]);
    curr_col++;
    if (curr_col >= size_of_problem){
      curr_row++;
      curr_col = curr_row;
    }
  }  
 
  Serial.write("!\n");
  Serial.flush();


}



void send_buttons_status(){
  
  Serial.write("b\n");
  Serial.flush();
  
  
  for(int curr_index = 0; curr_index<size_of_problem; curr_index++){
    Serial.println(state[curr_index]);
  } 
  
  
  
  Serial.write("!\n");
  Serial.flush();


}

void set_buttons_status(){
  
  Serial.write("k\n");
  Serial.flush();
  
  unsigned char bufferL[receivedByteLength];
  int num;
  int readNum;
  for(int curr_index = 0; curr_index<size_of_problem; curr_index++){
      while(Serial.available()<=0){}
       
      num = Serial.readBytes(bufferL, receivedByteLength);
      Serial.read();
      readNum =  (bufferL[0] << 8) | bufferL[1];
      state[curr_index] = readNum;
      Serial.println(readNum);
      Serial.flush();
    
  } 
  
  for (int i = 0; i<size_of_problem; i++){
     digitalWrite(ledPins[i], state[i]); 
  }
  Serial.write("!\n");
  Serial.flush();


}

void auto_mode_with_delay(){

  Serial.write("d\n");
  Serial.flush();
  unsigned char bufferL[receivedByteLength];
  int num;
  int readNum;
  
  //Reading first number --> Delay
  while(Serial.available()<=0){} 
  num = Serial.readBytes(bufferL, receivedByteLength);
  Serial.read();
  readNum =  (bufferL[0] << 8) | bufferL[1];
  timeOfdelayForAuto = readNum;
  Serial.println(readNum);
  Serial.flush();
  
  //Reading second number --> number of iterations
  while(Serial.available()<=0){} 
  num = Serial.readBytes(bufferL, receivedByteLength);
  Serial.read();
  readNum =  (bufferL[0] << 8) | bufferL[1];
  numOfIterations = readNum;
  Serial.println(readNum);
  Serial.flush();

  autoSolMode_V2();
  
  //get back to default values
  timeOfdelayForAuto = 100; 
  numOfIterations = 50;
  
  //Serial.println(fitness);
  Serial.write("!\n");
  Serial.flush();




}

void blink_hint(){
  Serial.write("u\n");
  Serial.flush();
  unsigned char bufferL[receivedByteLength];
  while(Serial.available()<=0){} 
  int num = Serial.readBytes(bufferL, receivedByteLength);
  Serial.read();
  int readNum =  (bufferL[0] << 8) | bufferL[1];
  
  if (readNum <0){
   for (int j = 0; j<3; j++){
      for (int i = 0; i<size_of_problem; i++){
        digitalWrite(ledPins[i], LOW); 
      }
      delay(300);
      for (int i = 0; i<size_of_problem; i++){
        digitalWrite(ledPins[i], state[i]); 
      } 
      delay(300);
    }
     
  }
  else
  {
    for (int j = 0; j<3; j++){
      
      digitalWrite(ledPins[readNum], LOW); 
      delay(300);
      digitalWrite(ledPins[readNum], HIGH); 
      delay(300);
    }
    
    digitalWrite(ledPins[readNum], state[readNum]);
 }
  
}
void autoSolMode_V3(){
 int randNumber1;
 autoModeIndicator = 1; 
 for (int k = 0; k <size_of_problem; k++){
  if(   k%2 == 0)
  {
    state[k] = solPosSpace[k];
  }
  else 
  {
    state[k] = !solPosSpace[k];
  }
  
  
  digitalWrite(ledPins[k], state[k] );
}
 updateFitness();
 scaleFitness();
  for (int i = 0; i <size_of_problem-1; i++ ){
    for (int j = 0; j <numOfIterations/(i+1) ; j++ ){
      for (int k = i+1; k <size_of_problem; k++){
        
        randNumber1 = random(100);
        if(   randNumber1%2 == 0){
          state[k] = !digitalRead(ledPins[k]);
          digitalWrite(ledPins[k], !digitalRead(ledPins[k]) ); 
  
        }
      }
     
    updateFitness();
    scaleFitness();
    delay(timeOfdelayForAuto);
    }
    
  
  state[i+1] = solPosSpace[i+1];
  digitalWrite(ledPins[i+1],  state[i+1] ); 
  }

  
 
 updateFitness();
 scaleFitness();
 autoModeIndicator = 0; 


}




void autoSolMode_V2(){
 int randNumber1;
 int randNumber2;
 autoModeIndicator = 1; 
 for (int k = 0; k <size_of_problem; k++){
  if(   k%2 == 0)
  {
    state[k] = solPosSpace[k];
  }
  else 
  {
    state[k] = !solPosSpace[k];
  }
  
  
  digitalWrite(ledPins[k], state[k] );
}
 updateFitness();
 scaleFitness();
 int iteratorValue = max(1, int(numOfIterations/size_of_problem) );

  for (int i = 1; i <size_of_problem; i++ ){
    for (int j = 0; j <numOfIterations-(iteratorValue*i) ; j++ ){
        for (int k = i; k <size_of_problem; k++){
          
         randNumber1 = random(100); 
         if(   randNumber1%2 == 0){
          state[k] = !digitalRead(ledPins[k]);
          digitalWrite(ledPins[k], !digitalRead(ledPins[k]) ); 
  
        }
      }
     
    updateFitness();
    scaleFitness();
    delay(timeOfdelayForAuto);
    }
    
  
  state[i] = solPosSpace[i];
  digitalWrite(ledPins[i],  state[i] ); 
  }

  
 
 updateFitness();
 scaleFitness();
 autoModeIndicator = 0; 


}
